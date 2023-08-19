cert_arn="alb.ingress.kubernetes.io/certificate-arn"
acm_arn="arn:aws:acm:ap-east-1:xxxxx:certificate/1111,arn:aws:acm:ap-east-1:xxxxxx:certificate/222222222"
ingress_file_path="/ingress"
api_version_old="extensions/v1beta1"
api_version_new="networking.k8s.io/v1"
fs=`grep -ri $cert_arn $ingress_file_path|grep -v replace-acm.sh |awk -F: '{print $1}'`

for f in $fs; do
    sed -i 's#".m.vickeywu#"*.m.vickeywu#g' $f
    sed -i 's#".vickeywu#"*.vickeywu#g' $f
    sed -i "s#$api_version_old#$api_version_new#g" $f
    sed -i "s#${cert_arn}.*#${cert_arn}: $acm_arn#g" $f
    sed -i 's#/\*#/#g' $f
    sed -E -i "s#(.*)backend#\1pathType: Prefix\n\1backend#g" $f
    sed -E -i "s#(.*)serviceName#\1service:\n\1  name#g" $f
    sed -E -i "s#(.*)servicePort:#\1  port:\n\1    number:#g" $f
done