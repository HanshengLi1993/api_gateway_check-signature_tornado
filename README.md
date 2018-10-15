#                         签名检查服务器端设计

## 项目背景

为了实现通过API将一些不太重要的，可以接受延时处理的实时生产数据通过服务器端验证消息的有效性后将数据插入消息队列中，以供之后接规则引擎简单处理数据在将数据存入相应数据库中。

本项目的定位是实现API签名校验，并将消息插入rabbit消息队列中。

## 设计思路

### 签名校验



#### 方案一：

1. 首先验证 timestamp是否过期，证明请求是在最近30min被发出的  对比与服务器的时间差
2.  再验证 nonce是否已经有了，证明这个请求不是30min内的重放请求 对比redis的nonce的键值是否存在，若不存在则将nonce存入redis中
3.  最后验证 sign签名是否合理，证明请求参数没有被中途篡改 获取私钥对请求签名，对比签名是否有修改

#### 方案二：

1. 首先验证 sign签名是否合理，证明请求参数没有被中途篡改 获取私钥对请求签名，对比签名是否有修改
2. 再验证 timestamp是否过期，证明请求是在最近30min被发出的  对比与服务器的时间差
3. 最后验证 nonce是否已经有了，证明这个请求不是30min内的重放请求 对比redis的nonce的键值是否存在

#### 方案三：

1. 首先验证 timestamp是否过期，证明请求是在最近30min被发出的  对比与服务器的时间差
2. 再验证 nonce是否已经有了，证明这个请求不是30min内的重放请求 对比redis的nonce的键值是否存
3. 最后验证 sign签名是否合理，证明请求参数没有被中途篡改 获取私钥对请求签名，对比签名是否有修改
4. 若 2中nonce没有且3中签名验证通过，则将新的nonce存入redis中



redis高效使用
阿里云Redis开发规范：https://yq.aliyun.com/articles/531067

redis的内存碎片

使用hash存储nonce信息，瓶颈在于hash个数不建议超过5000个。否则会出现bigkey问题，会产生一系列危害：内存偏移、网络流量大、慢查询等。

redis的信息在频繁删除，新增的前提下，将nonce的存储redis与appkey存储分离，将其集中到另一个redis集群上会比较好。一是在固定长度的数据可以避免内存碎片的产生，同时在设计key时不需要加入过多的标识符，减少key的长度，减少内存占用。



内存碎片是Redis在分配、回收物理内存过程中产生的。例如，如果对数据的更改频繁，而且数据之间的大小相差很大，可能导致redis释放的空间在物理内存中并没有释放，但redis又无法有效利用，这就形成了内存碎片。内存碎片不会统计在used_memory中。

内存碎片的产生与对数据进行的操作、数据的特点等都有关；此外，与使用的内存分配器也有关系：如果内存分配器设计合理，可以尽可能的减少内存碎片的产生。后面将要说到的jemalloc便在控制内存碎片方面做的很好。

如果Redis服务器中的内存碎片已经很大，可以通过安全重启的方式减小内存碎片：因为重启之后，Redis重新从备份文件中读取数据，在内存中进行重排，为每个数据重新选择合适的内存单元，减小内存碎片。

redis 过期时间打散

使用连接池连接redis





**Tornado的性能改善(一)：线程池的使用**

编辑于:2016-07-18

导语

*Tornado是一款优秀的开源Web框架，其简单易用，性能卓越等特性受到开发者的青睐。但是由于Tornado的单线程结构，假如执行耗时任务，此时线程则会阻塞，无法响应其他请求。下面就我对Tornado使用的经验，对其性能作出改善。*

**一. 线程池提高并发处理量**

*1. 使用Tornado自带的concurrent的语法糖run_on_executor。*

*2. 使用Python自带的concurrent的ThreadPoolExecutor线程池库。*

代码区间

from tornado.concurrent import run_on_executor

from concurrent.futures import ThreadPoolExecutor

import time

class Test():

executor = ThreadPoolExecutor(10)       #set up a threadpool

@run_on_executor

def longTimeTask():

print "go to sleep"

time.sleep(20)      #go to sleep

print "wake up"

if __name__ == "__main__":

test = Test()

test.longTimeTask()

print "print very soon"

上述例子当中，executor为初始化的线程池对象，而Test类中的longTimeTask被语法糖run_on_executor包裹，将该函数的执行传递给线程池executor的线程执行，优化了处理耗时性任务，以致达到不阻塞主线程的效果。

其实，上述的采用线程池优化并不是最优方案。耗时任务，通常涉及IO，其中常见的操作即是写日志，写数据库等数据持久化操作。此时我们更可以采取分布式任务队列的方式来进行优化。常见的有Celery + RabbitMq + Redis方案构建分布式任务队列系统。











