"""Transaction Throughput Performance Test (Synthetic)
"""
import time, random
from monitoring.latency_profiler import time_block

@time_block('inference_batch')
def fake_inference(batch_size):
    time.sleep(0.01)  # simulate work
    return [random.random() for _ in range(batch_size)]

def main():
    for batch in [100,500,1000,2000]:
        scores = fake_inference(batch)
        print({'batch':batch,'avg_score':sum(scores)/len(scores)})

if __name__=='__main__':
    main()
