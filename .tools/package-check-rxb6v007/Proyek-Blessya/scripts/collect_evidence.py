"""Jalankan percobaan laporan dan simpan data aktual tanpa dependensi tambahan."""
import json
import platform
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduling.models import Process
from src.scheduling.algorithms import fcfs, round_robin
from src.ipc.producer_consumer import run_demo

root=Path(__file__).resolve().parents[1]
sample=[Process('P1',0,5),Process('P2',1,3),Process('P3',2,1)]
data={'date':datetime.now(timezone(timedelta(hours=7))).date().isoformat(),'timezone':'Asia/Jakarta','python':platform.python_version(),
      'platform':platform.platform(), 'sample':[vars(p) for p in sample],
      'fcfs':fcfs(sample).to_dict(), 'round_robin':{str(q):round_robin(sample,q).to_dict() for q in (1,2,3,5,10,20)},
      'idle':fcfs([Process('P1',5,3)]).to_dict(),
      'convoy':{name:fn([Process('P1',0,24),Process('P2',0,3),Process('P3',0,3)]).to_dict()
                for name,fn in [('fcfs',fcfs),('rr2',lambda ps:round_robin(ps,2))]},
      'producer_consumer':{}}
for name,delays in [('produsen_cepat',(0.01,0.08)),('konsumen_cepat',(0.08,0.01)),('seimbang',(0.04,0.04))]:
    runs=[]
    for i in range(5):
        result=run_demo(capacity=5,n_producers=1,n_consumers=1,items_each=8,
                        produce_delay=delays[0],consume_delay=delays[1])
        assert result['completed'] and not result['stuck_threads']
        assert all(0<=e['buffer_size']<=5 and e['buffer_size']==len(e['items']) for e in result['events'])
        runs.append(result)
    data['producer_consumer'][name]={'produce_ms':round(delays[0]*1000),'consume_ms':round(delays[1]*1000),'runs':runs}
out=root/'docs/evidence/experiments.json'
out.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
print('Evidence:',out)
for q,r in data['round_robin'].items(): print('RR',q,r['summary'])
for name,scenario in data['producer_consumer'].items():
    print(name,[(r['blocked_producers'],r['blocked_consumers'],r['peak_buffer_usage']) for r in scenario['runs']])
