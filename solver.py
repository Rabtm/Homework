import os.path
from prob_builder import *
from typing import List
import time
import pickle

PENALTY = 1000000

def rule_solver(instance: Prob_Instance) -> dict:
    print('Solver Start')
    solution = {}
    solution['Problem'] = instance.deepcopy()

    req_list = instance.req_list
    req: Request
    for req in req_list:
        req.initialize()

    stn_list = instance.stn_list
    stn: Station
    for stn in stn_list:
        stn.initialize()

    total_algorithm_start = time.time()

    # ===================================================================================================
    distance_start = time.time()
    if not os.path.exists('dist.p'):
        distance_dic = {}

        for req in req_list:
            for st in stn_list:
                distance_dic[dic_key(req.loc, st.loc)] = get_distance_lat(req.loc, st.loc)
                distance_dic[dic_key(st.loc, req.loc)] = get_distance_lat(st.loc, req.loc)

        for req1 in req_list:
            for req2 in req_list:
                if req1.id != req2.id:
                    distance_dic[dic_key(req1.loc, req2.loc)] = get_distance_lat(req1.loc, req2.loc)
                    distance_dic[dic_key(req2.loc, req1.loc)] = get_distance_lat(req2.loc, req1.loc)


        with open('dist.p', 'wb') as file:
            pickle.dump(distance_dic, file)

    else:
        with open('dist.p', 'rb') as file:
            distance_dic = pickle.load(file)

        for req in req_list:
            for st in stn_list:
                if dic_key(req.loc, st.loc) not in distance_dic:
                    distance_dic[dic_key(req.loc, st.loc)] = get_distance_lat(req.loc, st.loc)
                    distance_dic[dic_key(st.loc, req.loc)] = get_distance_lat(st.loc, req.loc)

        for req1 in req_list:
            for req2 in req_list:
                if req1.id != req2.id and (dic_key(req1.loc, req2.loc) not in distance_dic):
                    distance_dic[dic_key(req1.loc, req2.loc)] = get_distance_lat(req1.loc, req2.loc)
                    distance_dic[dic_key(req2.loc, req1.loc)] = get_distance_lat(req2.loc, req1.loc)

        with open('dist.p', 'wb') as file:
            pickle.dump(distance_dic, file)

    distance_end = time.time()
# ====================================================================================================================

    def priority(target_list: List[Request], station_list: List[Station]):
        pri_dic = {}
        for req in target_list:
            for stn in station_list:
                if stn.doable(req):
                    if isinstance(stn, MovableStation):
                        try:
                            dist = distance_dic[dic_key(stn.loc, req.loc)]  # 위의 딕셔너리에서 값 바로 가져오기
                        except Exception:
                            dist = (get_distance_lat(stn.loc, req.loc))  # 위의 딕셔너리에서 값 바로 가져오기
                    else:
                        try:
                            dist = distance_dic[dic_key(req.loc, stn.loc)] # 위의 딕셔너리에서 값 바로 가져오기
                        except Exception:
                            dist = (get_distance_lat(req.loc, stn.loc)) # 위의 딕셔너리에서 값 바로 가져오기
                else:
                    dist = PENALTY

                pri_dic[dist] = [req, stn]

        minimum = min(pri_dic.keys())

        return pri_dic[minimum][0], pri_dic[minimum][1]
# ====================================================================================================================

    while any(req.done is False for req in req_list):
        not_completed_reqs = list(filter(lambda x: (x.done is False), req_list))
        servable_stn = list(filter(lambda x: x.can_recharge is True, stn_list))
        pri_req, pri_stn = priority(not_completed_reqs,servable_stn)

        try:
             pri_stn.recharge(pri_req)
        except Exception:
            raise Exception('Invalid Logic')
            break

    solution['Snapshop_Requests'] = req_list
    solution['Snapshop_Stations'] = stn_list

    maximum = 0
    for stn in stn_list:
        if stn.measures['total_time'] > maximum:
            maximum = stn.measures['total_time']

    solution['Objective'] = maximum

    total_algorithm_end = time.time()

    print(f"total_time :{total_algorithm_end - total_algorithm_start:.4f} ")
    print(f"distance_time : {distance_end - distance_start:.4f}")
    print(f"algorithm_time : {(total_algorithm_end - total_algorithm_start) - (distance_end - distance_start):.4f}")

    return solution

