for deploy in $(kubectl get deploy -n default -o name); do
  kubectl scale $deploy --replicas=0
  #echo $deploy
done