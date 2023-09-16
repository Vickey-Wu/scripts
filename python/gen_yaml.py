import os
import yaml

## all_images.txt

"""
svc_name, ecr:image_tag
"""
# svc yaml
"""
apiVersion: v1
kind: Service
metadata:
  name: GIT_REPO_NAME
  labels:
    app: GIT_REPO_NAME
  annotations:
    boot.spring.io/actuator: http://:8081/actuator
    prometheus.io/scrape: 'true'
    prometheus.io.scrape/springboot: 'true'
    prometheus.io/path: '/actuator/prometheus'
    prometheus.io/port: '8081'
spec:
  selector:
    app: GIT_REPO_NAME
  type: ClusterIP
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  - name: manageport
    port: 8081
    targetPort: 8081
"""
## deployment.yaml
"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: GIT_REPO_NAME
spec:
  selector:
    matchLabels:
      app: GIT_REPO_NAME
  replicas: POD_NUM
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: GIT_REPO_NAME
        version: GIT_REPO_VERSION
      annotations:
        prometheus.io.scrape/springboot: 'true'
        prometheus.io/path: '/actuator/prometheus'
        prometheus.io/port: '8081'
    spec:
      serviceAccountName: placeholder
      volumes:
        - name: skywalking-agent
          emptyDir: { }
        - name: micro-svc-pv
          persistentVolumeClaim:
            claimName: micro-svc-pv
      initContainers:
      - name: agent-container
        image: xxx.ecr.ap-east-1.amazonaws.com/skywalking-java-agent:8.7.0-alpine
        volumeMounts:
          - name: skywalking-agent
            mountPath: /agent
        command: [ "/bin/sh" ]
        args: [ "-c", "cp -R /skywalking/agent /agent/" ]
      ## default 30s
      terminationGracePeriodSeconds: 120
      containers:
      - image: IMAGE_NAME
        lifecycle:
          preStop:
            exec:
              command: ['/bin/sh','-c', '/bin/sleep 3; HI=`hostname -i`; curl -X PUT "NACOS_SERVER/nacos/v1/ns/instance?namespaceId=NACOS_NAMESPACE&groupName=DEFAULT_GROUP&ip=\${HI}&port=8080&serviceName=NACOS_SERVICE_NAME&clusterName=DEFAULT&enabled=false"; sleep 32;curl -X POST "127.0.0.1:8081/actuator/shutdown";sleep 3;']
        imagePullPolicy: IfNotPresent
        name: GIT_REPO_NAME
        ports:
        - containerPort: 8080
          name: project-port
        - containerPort: 8081
          name: manageport
        volumeMounts:
          - name: skywalking-agent
            mountPath: /skywalking
          - name: micro-svc-pv
            mountPath: /data/micro-svc-pv
        env:
          - name: ENV_NAME
            value: AWS-ENV-NAME
          - name: JAVA_TOOL_OPTIONS
            value: "-javaagent:/skywalking/agent/skywalking-agent.jar"
          - name: SW_AGENT_COLLECTOR_BACKEND_SERVICES
            value: skywalking-oap.kube-ops.svc:11800
          - name: SW_GRPC_LOG_SERVER_HOST
            value: skywalking-oap.kube-ops.svc
          - name: SW_AGENT_NAME
            value: GIT_REPO_NAME
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8081
          initialDelaySeconds: 50
          periodSeconds: 10
          failureThreshold: 30
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8081
          initialDelaySeconds: 50
          periodSeconds: 10
          failureThreshold: 30
        #resources:
          # requests:
          #   memory: "1000Mi"
          #   cpu: "200m"
          # limits:
          #  memory: "2500Mi"
          #  cpu: "1500m"
"""

def backend_yaml():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "deployment.yaml")) as deployment:
        job_deployment = yaml.safe_load(deployment)
    with open(os.path.join(dir_path, "svc.yaml")) as svc:
        job_svc = yaml.safe_load(svc)
    sa_list = ['app', 'base']
    with open(os.path.join(dir_path, "all_images.txt")) as ai:
        for i in ai:
            GIT_REPO_NAME = i.strip().split(",")[0]
            if "project" in GIT_REPO_NAME or "mobile" in GIT_REPO_NAME:
                continue
            IMAGE_NAME = i.strip().split(",")[1]
            job_deployment['metadata']['name'] = GIT_REPO_NAME
            job_deployment['spec']['selector']['matchLabels']['app'] = GIT_REPO_NAME
            job_deployment['spec']['template']['metadata']['labels']['app'] = GIT_REPO_NAME
            job_deployment['spec']['template']['spec']['containers'][0]['env'][4]["value"] = GIT_REPO_NAME
            job_deployment['spec']['template']['spec']['containers'][0]['name'] = GIT_REPO_NAME
            if GIT_REPO_NAME in sa_list:
                job_deployment['spec']['template']['spec']['serviceAccountName'] = GIT_REPO_NAME
            else:
                job_deployment['spec']['template']['spec']['serviceAccountName'] = "placeholder"
            job_deployment['spec']['template']['spec']['containers'][0]['image'] = IMAGE_NAME
            nacos_cmd = "http://nacos.vickeywu.com:8848/nacos/v1/ns/instance?namespaceId=aws-prod&groupName=DEFAULT_GROUP&ip=${HI}&port=8080&serviceName=" + \
                GIT_REPO_NAME + "&clusterName=DEFAULT&enabled=false"
            command = f'/bin/sleep 3; HI=`hostname -i`; curl -X PUT "{nacos_cmd}" sleep 32;curl -X POST "127.0.0.1:8081/actuator/shutdown";sleep 3;'
            job_deployment['spec']['template']['spec']['containers'][0]['lifecycle']['preStop']['exec']['command'][2] = command

            deployment_path = os.path.join(
                dir_path, f"./all_images/deployment-{GIT_REPO_NAME}.yaml")
            with open(deployment_path, 'w') as df:
                yaml.dump(job_deployment, df)

            job_svc['metadata']['name'] = GIT_REPO_NAME
            job_svc['metadata']['labels']['app'] = GIT_REPO_NAME
            job_svc['spec']['selector']['app'] = GIT_REPO_NAME
            svc_path = os.path.join(
                dir_path, f"./all_images/svc-{GIT_REPO_NAME}.yaml")
            with open(svc_path, 'w') as sf:
                yaml.dump(job_svc, sf)


backend_yaml()
