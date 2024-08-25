import json
import math

PRICE_PER_GBS_OF_LAMBDA = 0.0000166667
GBS = 8

path_to_file = 'costs.json'

with open(path_to_file) as json_file:
    current_costs = json.load(json_file)
    PRICES = {
        "s3:GetObject": current_costs['s3']['1M_read_requests'] / 1000000,
        "s3:PutObject": current_costs['s3']['1M_write_requests'] / 1000000,
        "s3:DeleteObject": 0,  # current_costs['s3']['1M_write_requests'] / 1000000,
        "kinesis:PutRecord": current_costs['kinesis']['1M_write_requests'] / 1000000,
        "efs:write": current_costs['efs']['1gb_write'] / 1000 / 250,  # 4kB block
        "efs:listdir": current_costs['efs']['1gb_read'] / 1000 / 250,  # 4kB block
        "efs:read": current_costs['efs']['1gb_read'] / 1000 / 250,  # 4kB block
        "efs:delete": 0,  # current_costs['efs']['1gb_write'] / 1000 / 250,  # 4kB block
        "sqs:ReceiveMessage": current_costs['sqs']['1gb_read'] / 1000000000,
        "dynamodb:PutItem": current_costs['dynamodb']['1M_write_requests'] / 1000 / 250,  # 4kB block
        "dynamodb:GetItem": current_costs['dynamodb']['1M_read_requests'] / 1000 / 250,  # 4kB block
        "dynamodb:DeleteItem": 0,  # current_costs['dynamodb']['1M_write_requests'] / 1000 / 250,  # 4kB block
        "redis:get": current_costs['elasticacheforredis']['1M_ecpus'] / 1000000,  # 1 ECPU = 1kB
        "redis:set": current_costs['elasticacheforredis']['1M_ecpus'] / 1000000,  # 1 ECPU = 1kB
        "redis:delete": 0
    }


def divide_by_4kb(value):
    return math.ceil(value / 4000)


def sum_usage(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}


def get_usage_sum(data):
    return data['usage']


def calculate_cost_for_s3(data):
    usages = get_usage_sum(data)
    sum = 0
    for key, value in usages.items():
        sum += value * PRICES[key]
    return sum


def calculate_cost_for_sqs(message_size, data):
    return 2 * message_size * PRICES['sqs:ReceiveMessage']


def calculate_cost_for_relayfargate(message_size, data):
    return data['total_time'] / 3600 * current_costs['relayfargate']['instance_per_hour']


def calculate_cost_for_p2pfargate(message_size, data):
    return (data['total_time']) / 3600 * current_costs['p2pfargate']['instance_per_hour']


def calculate_cost_for_relay(message_size, data):
    return data['total_time'] / 3600 * current_costs['relayec2']['instance_per_hour']


def calculate_cost_for_p2p(message_size, data):
    return (data['total_time']) / 3600 * current_costs['p2pec2']['instance_per_hour']


def calculate_cost_for_redisserverless(message_size, data):
    usages = get_usage_sum(data)
    sum = 0
    for key, value in usages.items():
        sum += value / 1000 * PRICES[key]
    return sum


def calculate_cost_for_redis(message_size, data):
    return (data['total_time']) / 3600 * current_costs['redisec2']['instance_per_hour']


def calculate_cost_for_kinesis(message_size, data):
    shard_cost = current_costs['kinesis']['shard_per_hour'] * data['total_time'] / 3600
    put_cost = 2 * PRICES['kinesis:PutRecord']

    return shard_cost + put_cost


def calculate_cost_for_efs(message_size, data):
    _4kb_packs = divide_by_4kb(message_size)
    write_costs = 2 * _4kb_packs * PRICES['efs:write']
    usages = get_usage_sum(data)

    read_costs = usages['efs:read'] * PRICES['efs:read']
    list_costs = usages['efs:listdir'] * PRICES['efs:listdir']

    return write_costs + read_costs + list_costs


def calculate_cost_for_dynamodb(message_size, data):
    _4kb_packs = divide_by_4kb(message_size)
    write_costs = 2 * _4kb_packs * PRICES['dynamodb:PutItem']
    read_costs = _4kb_packs * PRICES['dynamodb:GetItem']

    return write_costs + read_costs


def estimate(method, message_size, data):
    data['total_time'] = data['total_time'] if 'p2p' not in method else data['total_time'] - 1

    result = {
        'method': method,
        'message_size': message_size,
        'time': data['total_time'],
        'lambda_cost': data['total_time'] * PRICE_PER_GBS_OF_LAMBDA * GBS
    }

    match method:
        case 's3':
            result['cost'] = calculate_cost_for_s3(data)
        case 'sqs':
            result['cost'] = calculate_cost_for_sqs(message_size, data)
        case 'relayfargate':
            result['cost'] = calculate_cost_for_relayfargate(message_size, data)
        case 'p2pfargate':
            result['cost'] = calculate_cost_for_p2pfargate(message_size, data)
        case 'relay':
            result['cost'] = calculate_cost_for_relay(message_size, data)
        case 'p2p':
            result['cost'] = calculate_cost_for_p2p(message_size, data)
        case 'redis':
            result['cost'] = calculate_cost_for_redis(message_size, data)
        case 'redisserverless':
            result['cost'] = calculate_cost_for_redisserverless(message_size, data)
        case 'kinesis':
            result['cost'] = calculate_cost_for_kinesis(message_size, data)
        case 'efs':
            result['cost'] = calculate_cost_for_efs(message_size, data)
        case 'dynamodb':
            result['cost'] = calculate_cost_for_dynamodb(message_size, data)

    return result

