"""Analisis trace tersimpan: interval kejadian bukan durasi Event.wait murni."""
from pathlib import Path
import hashlib
import json
import statistics

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'docs/evidence/experiments.json'
data=json.loads(source.read_text(encoding='utf-8'))
summaries=[]
for scenario_name,scenario in data['producer_consumer'].items():
    for index,run in enumerate(scenario['runs'],1):
        events=run['events']
        queue=[]
        counts={'PRODUKSI':0,'KONSUMSI':0,'prod_wait':0,'cons_wait':0}
        for event in events:
            if event['action']=='PRODUKSI':
                counts['PRODUKSI']+=1;queue.append(event['detail'].split()[-1])
            elif event['action']=='KONSUMSI':
                counts['KONSUMSI']+=1
                assert queue.pop(0)==event['detail'].split()[-1]
            elif event['action']=='BLOKIR':
                counts['prod_wait' if event['actor'].startswith('Produsen') else 'cons_wait']+=1
            assert queue==event['items'] and len(queue)==event['buffer_size']
            assert 0<=len(queue)<=run['capacity']
        assert counts['PRODUKSI']==run['produced']==8
        assert counts['KONSUMSI']==run['consumed']==8
        assert counts['prod_wait']==run['blocked_producers']
        assert counts['cons_wait']==run['blocked_consumers']
        assert not queue and run['completed'] and not run['stuck_threads']
        production=[e['t'] for e in events if e['action']=='PRODUKSI']
        first_intervals=[round(b-a,2) for a,b in zip(production[:4],production[1:5])]
        summaries.append({'scenario':scenario_name,'run':index,
            'requested_produce_ms':scenario['produce_ms'],
            'requested_consume_ms':scenario['consume_ms'],
            'first_five_production_timestamps_ms':production[:5],
            'first_four_production_intervals_ms':first_intervals,
            'interval_min_ms':min(first_intervals),'interval_max_ms':max(first_intervals),
            'interval_mean_ms':round(statistics.mean(first_intervals),2),
            'producer_blocks_recounted':counts['prod_wait'],
            'consumer_blocks_recounted':counts['cons_wait']})
result={'source':'docs/evidence/experiments.json',
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_date':data['date'],'platform':data['platform'],'python':data['python'],
        'method':'Selisih empat pasang timestamp PRODUKSI berurutan pada lima produksi pertama; bukan pengukuran langsung pemanggilan wait().',
        'validated_runs':len(summaries),'runs':summaries}
(ROOT/'docs/evidence/timing-analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
for row in summaries[:5]:print(row)
print('Jumlah run yang direkonstruksi:',len(summaries))
