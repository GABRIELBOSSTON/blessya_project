"""Regresi inti: contoh manual, input buruk, konsistensi log dan penghentian thread."""
import sys
import json
import threading
import tempfile
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduling.models import Process
from src.scheduling.algorithms import fcfs, round_robin, compare_all
from src.ipc.producer_consumer import run_demo, BoundedBuffer
from src.server import api_scheduling, api_producer_consumer, Handler


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.ps = [Process('P1', 0, 5), Process('P2', 1, 3), Process('P3', 2, 1)]

    def test_fcfs_manual(self):
        r = fcfs(self.ps)
        self.assertEqual([(s.pid, s.start, s.end) for s in r.timeline], [('P1',0,5),('P2',5,8),('P3',8,9)])
        self.assertEqual([(m.waiting,m.turnaround,m.response) for m in r.metrics], [(0,5,0),(4,7,4),(6,7,6)])
        self.assertEqual((r.avg_waiting,r.avg_turnaround,r.context_switches),(3.33,6.33,2))

    def test_rr_manual_boundary_arrival(self):
        r = round_robin(self.ps,2)
        self.assertEqual([(s.pid,s.start,s.end) for s in r.timeline], [('P1',0,2),('P2',2,4),('P3',4,5),('P1',5,7),('P2',7,8),('P1',8,9)])
        self.assertEqual([(m.waiting,m.turnaround,m.response) for m in r.metrics], [(4,9,0),(4,7,1),(2,3,2)])
        self.assertEqual(r.context_switches,5)

    def test_rr_single_process_not_switch(self):
        r=round_robin([Process('A',0,5)],2)
        self.assertEqual([s.duration for s in r.timeline],[2,2,1])
        self.assertEqual(r.context_switches,0)

    def test_rr_large_quantum_fcfs(self):
        a,b=fcfs(self.ps),round_robin(self.ps,10)
        self.assertEqual(a.metrics,b.metrics)
        self.assertEqual(a.context_switches,b.context_switches)

    def test_idle_not_switch(self):
        for r in compare_all([Process('A',2,1),Process('B',5,1)]):
            self.assertEqual(r.context_switches,0)
            self.assertEqual(r.total_time,6)
            self.assertEqual(r.avg_waiting,0)

    def test_arrival_tie_lexical(self):
        self.assertEqual([s.pid for s in fcfs([Process('P2',0,1),Process('P10',0,1)]).timeline], ['P10','P2'])

    def test_duplicate_direct_call(self):
        for fn in (fcfs,round_robin):
            with self.assertRaises(ValueError): fn([Process('A',0,1),Process('A',0,2)])

    def test_reserved_id(self):
        for pid in ('IDLE','idle','Idle'):
            with self.assertRaises(ValueError): Process(pid,0,1)

    def test_quantum_type(self):
        for q in (0,-1,1.5,True):
            with self.assertRaises(ValueError): round_robin(self.ps,q)

    def test_invalid_numbers_api(self):
        for value in (-1,0,51,1.5,True,None,'abc','2.5'):
            with self.assertRaises(ValueError): api_scheduling({'processes':[{'burst':value}]})
        for value in (-1,101,1.5,False):
            with self.assertRaises(ValueError): api_scheduling({'processes':[{'arrival':value,'burst':1}]})

    def test_bad_process_shapes(self):
        for data in ([],None,{},'bad',[None],[42],[{} , {'pid':'P1'}]):
            with self.assertRaises(ValueError): api_scheduling({'processes':data})

    def test_single_api_has_result(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='web-probe-',dir=root) as folder:
            Path(folder,'probe.txt').write_text('must not be served',encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                url=f'http://127.0.0.1:{server.server_port}/../{Path(folder).name}/probe.txt'
                with self.assertRaises(urllib.error.HTTPError) as caught: urllib.request.urlopen(url)
                self.assertEqual(caught.exception.code,403)
            finally:
                server.shutdown();server.server_close();worker.join()
        result=api_scheduling({'algorithm':'fcfs','processes':[{'burst':2}]})
        self.assertEqual(result['mode'],'single')
        self.assertEqual(result['results'][0]['summary']['avg_waiting'],0)


class HTTPRobustnessTests(unittest.TestCase):
    def test_complex_json_rejected_and_server_recovers(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            payloads=[b'{"data":'+b'['*10000+b'0'+b']'*10000+b'}',
                      b'{"data":'+b'9'*5000+b'}']
            for payload in payloads:
                with self.subTest(size=len(payload)):
                    request=urllib.request.Request(base+'/api/scheduling',data=payload,
                        headers={'Content-Type':'application/json'})
                    with self.assertRaises(urllib.error.HTTPError) as caught:
                        urllib.request.urlopen(request,timeout=3)
                    self.assertEqual(caught.exception.code,400)
                    self.assertIn('error',json.loads(caught.exception.read()))
            request=urllib.request.Request(base+'/api/scheduling',
                data=b'{"algorithm":"fcfs","processes":[{"burst":2}]}',
                headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=3) as response:
                result=json.loads(response.read())
            self.assertEqual(result['results'][0]['summary']['total_time'],2)
        finally:
            server.shutdown();server.server_close();worker.join()


class BufferTests(unittest.TestCase):
    def assert_trace(self,r):
        self.assertTrue(r['completed'],r['errors'])
        self.assertEqual(r['stuck_threads'],[])
        self.assertEqual(r['leftover_in_buffer'],0)
        queue=[]; produced=[]; consumed=[]
        for e in r['events']:
            if e['action']=='PRODUKSI':
                item=e['detail'].split()[-1]; queue.append(item); produced.append(item)
            elif e['action']=='KONSUMSI':
                item=e['detail'].split()[-1]; self.assertEqual(queue.pop(0),item); consumed.append(item)
            self.assertEqual(e['items'],queue)
            self.assertEqual(e['buffer_size'],len(queue))
            self.assertLessEqual(len(queue),r['capacity'])
        self.assertEqual(produced,consumed)
        self.assertEqual(len(produced),r['produced'])

    def test_fast_producer(self):
        r=run_demo(1,1,1,8,0,0.03)
        self.assert_trace(r); self.assertGreater(r['blocked_producers'],0)

    def test_fast_consumer(self):
        r=run_demo(2,1,1,8,0.03,0)
        self.assert_trace(r); self.assertGreater(r['blocked_consumers'],0)

    def test_multiple_workers_trace(self):
        for _ in range(6): self.assert_trace(run_demo(3,3,4,5,0,0))

    def test_more_consumers_than_items(self):
        self.assert_trace(run_demo(1,1,5,1,0,0))

    def test_timeout_cleans_threads(self):
        r=run_demo(1,1,1,12,0.1,0.1,timeout=0.01)
        self.assertFalse(r['completed']); self.assertTrue(r['errors'])
        self.assertEqual(r['stuck_threads'],[])
        self.assertFalse(any(t.name.startswith('PC-') for t in threading.enumerate()))

    def test_worker_error_cancels_peer(self):
        with patch.object(BoundedBuffer,'put',side_effect=RuntimeError('injected')):
            r=run_demo(1,1,1,2,0,0)
        self.assertFalse(r['completed']); self.assertIn('injected',r['errors'])
        self.assertEqual(r['stuck_threads'],[])

    def test_invalid_params(self):
        for kw in ({'n_consumers':0},{'n_producers':0},{'items_each':0},{'capacity':False},
                   {'produce_delay':-1},{'consume_delay':float('nan')},{'timeout':0}):
            with self.assertRaises(ValueError): run_demo(**kw)

    def test_api_strict_values(self):
        for kw in ({'capacity':0},{'items':1.5},{'producers':False},{'produce_ms':101}):
            with self.assertRaises(ValueError): api_producer_consumer(kw)


if __name__=='__main__': unittest.main(verbosity=2)
