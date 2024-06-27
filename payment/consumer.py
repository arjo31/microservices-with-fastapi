from main import redis, Order
import time

key = 'refund_completed'
group = 'payment_group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists')

while True:
    try:
        results = redis.xreadgroup(group, key, {key : '>'}, None)
        if results!=[]:
            for result in results:
                order = result[1][0][1]
                order = Order.get(order['pk'])
                order.status = 'refunded'
                order.save()
    except Exception as e:
        print(str(e))
    time.sleep(1)