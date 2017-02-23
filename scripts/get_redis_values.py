#!/usr/bin/env python
# coding: utf-8

import redis

redis_client = redis.StrictRedis(host="localhost", db=0)

for key in redis_client.keys():
    print redis_client.hgetall(key)
