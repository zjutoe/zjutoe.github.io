# AI Infra Day1 Distributed Data Parallel (DDP)
## 第一版：手动DDP
- 多进程启动：torchrun，每个进程对应一个rank，rank有global rank id、local rank id。所有rank属于同一个process group。
- 特点：模型参数共享、数据分布式处理。
- 数据同步时机：模型forward/backward之后，optimizer.step()之前。
- 数据同步方式：all_reduce，即各rank的数据加总，dist.all_reduce(..., op=dist.ReduceOp.SUM)，然后除以总rank数（world_size）取平均。
- 数据同步底层库：torch.distributed -> Nvidia Collective Communications Library (NCCL) 
- 参考代码：https://github.com/zjutoe/ml-lab/blob/master/experiments/ddp_minimal/train_manual_sync.py
## 第二版：自动DDP
- from torch.nn.parallel import DistributedDataParallel as DDP
- 封装：model = DDP(model, ...)
- 数据自动同步：在loss.backward()期间，DDP 已经通过 autograd hooks 等机制完成 gradient sync，所以在optimizer.step()之前，gradient已经同步了。
- optimizer.step()是每个rank本地执行的，不是分布式处理。
- bucket：DDP会把梯度数据拼成一个个桶，分组同步。
- computer-communication overlap: DDP会在loss.backward()一边计算的同时，一边把已经算完的bucket做同步传输。比如有10层网络，第10层算完、开始算第9层时，就可以把第10层的梯度数据做同步。
- 参考代码：https://github.com/zjutoe/ml-lab/blob/master/experiments/ddp_minimal/train_ddp.py
## 数据同步的不同方式
- broadcast：从一个rank发到其他rank
- all_reduce：所有rank共同参加运算，得到SUM、MAX等结果
- all_gather：把各个rank的数据收集起来，所有rank都得到完整copy，不做其他计算
- reduce_scatter：先reduce，再把结果切片，分配给不同rank
- （逻辑上）all_reduce = reduce_scatter + all_gather
