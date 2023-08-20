import json
import os

# """
# bcp_s3_role_relationship.txt
# upload	upload
# upload	user
# user	user
# """
# """
# bcp_policy.json
# {
# 	"Version": "2012-10-17",
# 	"Statement": [
# 		{
# 			"Effect": "Allow",
# 			"Principal": {
# 				"AWS": [
# 					"arn:aws:iam::111111111111:role/user",
# 					"arn:aws:iam::111111111111:role/upload",
# 					"arn:aws:iam::111111111111:role/EC2-CDN-Origin-Server"
# 				]
# 			},
# 			"Action": [
# 				"s3:Get*",
# 				"s3:List*"
# 			],
# 			"Resource": [
# 				"arn:aws:s3:::bucketname/*",
# 				"arn:aws:s3:::bucketname"
# 			]
# 		}
# 	]
# }
# """

def gen_bucket_role_dict():
    with open("bcp_s3_role_relationship.txt", "r") as f:
        tmp_dict = {}
        for i in f:
            tmp_data = i.strip().split("\t")
            if tmp_data[1] in tmp_dict.keys():
                tmp_dict[tmp_data[1]].append(tmp_data[0])
            else:
                tmp_dict[tmp_data[1]] = [tmp_data[0]]
    # print(tmp_dict)
    return tmp_dict


def gen_s3_policy():

    # 读取JSON文件
    with open('bcp_policy.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    # 修改key-value
    tmp_dict = gen_bucket_role_dict()
    for k, v in tmp_dict.items():
        tmp_role = ["arn:aws:iam::111111111111:role/EC2-CDN-Origin-Server"]
        for r in v:
            tmp_role.append(f"arn:aws:iam::111111111111:role/{r}")
        data['Statement'][0]['Principal']['AWS'] = tmp_role

        bucket_list = [f"arn:aws:s3:::{k}/*", f"arn:aws:s3:::{k}"]
        data['Statement'][0]['Resource'] = bucket_list

        # 生成新JSON文件
        dir_path = os.path.dirname(os.path.realpath(__file__))
        svc_path = os.path.join(
            dir_path, f"./all_images/{k}.json")
        with open(svc_path, 'w') as jf:
            json.dump(data, jf)


gen_s3_policy()
# gen_bucket_role_dict()
