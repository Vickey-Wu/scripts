import os


def gen_sa_cli():
    sa_list = ['user', 'admin']
    cluster_name = "bcp"
    account_id = "xxxx"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "sa_cli.sh"), "w") as f:
        for i in sa_list:
            cmd = f"eksctl create iamserviceaccount \
            --cluster={cluster_name} \
            --role-name={i} \
            --namespace=default \
            --name={i} \
            --attach-policy-arn=arn:aws:iam::{account_id}:policy/s3-policy-for-{i} \
            --approve"
            f.write(cmd + "\n")

gen_sa_cli()