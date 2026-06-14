import requests

token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIzMDUwMDIxOSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc4MDQ5NDM2NCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTk4NTg2Mjk4NjkiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJhYTE1NTc0YS0zYWM1LTQ3NDctYTRiOC1kMzYzMTVjZDFjMGIiLCJlbWFpbCI6IiIsImV4cCI6MTc4ODI3MDM2NH0.YH7gMEUFxnI6x8mLJ7Pv5o3JHkMD0TiwsvhULJPL0loaXVpH7suJ8WjjyCjXkZMN7l2B3L9pTYrZ0tqbga_0tw"
url = "https://mineru.net/api/v4/extract/task/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "files": [
        {"url":"https://static.cninfo.com.cn/finalpage/2025-11-28/1224831097.PDF", "data_id": "1224831097"}
    ],
    "model_version": "vlm"
}
try:
    response = requests.post(url,headers=header,json=data)
    if response.status_code == 200:
        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            print('batch_id:{}'.format(batch_id))
        else:
            print('submit task failed,reason:{}'.format(result["msg"]))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
except Exception as err:
    print(err)
result_url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"

result_response = requests.get(
    result_url,
    headers=header
)

print(result_response.json())