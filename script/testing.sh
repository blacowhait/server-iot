#!/bin/bash
# for mageran people who doenst want to check the testing for 1 app is completed
# and change to another app

# hanin 
ssh root@10.104.0.2 'systemctl restart postgresql.service'
sleep 10
ssh root@10.104.0.2 'cd /root/code/hanin/falcon_project && gunicorn -b 0.0.0.0:5000 app:api –reload' &
sleep 10
kill -9 $(pgrep ssh | tail -1)
./siege.sh hanin > result/hanin.txt
ssh root@10.104.0.2 'kill -2 $(pgrep 'gunicorn' | head -1)'
echo '>>>>>>>>>>>>>>> hanin done'

# alvin v2
ssh root@10.104.0.2 'systemctl restart postgresql.service'
sleep 10
ssh root@10.104.0.2 'python3 /root/code/alvin/SanicIOT/Token_v2/server.py' &
sleep 10
kill -9 $(pgrep ssh | tail -1)
./siege.sh alvinv2 > result/alvin_v2.txt
ssh root@10.104.0.2 'kill -2 $(pgrep 'python3' | head -1)'
echo '>>>>>>>>>>>>>>> alvin v2 done'
sleep 300

# alvin v1
ssh root@10.104.0.2 'systemctl restart postgresql.service'
sleep 10
ssh root@10.104.0.2 'python3 /root/code/alvin/SanicIOT/Token_v1/server.py' &
sleep 10
kill -9 $(pgrep ssh | tail -1)
./siege.sh alvinv1 > result/alvin_v1_1.txt
ssh root@10.104.0.2 'kill -2 $(pgrep 'python3' | head -1)'
echo '>>>>>>>>>>>>>>> alvin v1 done'
sleep 300