# cpmawscli
mainly for use via rundeck

```
usage: cpmawscli.py [-h] (--tag key value | --instance INSTANCE) [--dryrun]
                    [--exclude [EXCLUDE [EXCLUDE ...]]]
                    [--loglevel {debug,info,notice,warning,error,critical}]
                    [--aws_access_key_id AWS_ACCESS_KEY_ID]
                    [--aws_secret_access_key AWS_SECRET_ACCESS_KEY]
                    {Ec2,Rds} ...
```

example :
stop all rds instances with tag Env=integ except instance foo and instance bar
```
./cpmawscli.py  --tag Env integ --except foo bar --aws_secret_access_key='xxxxxx' --aws_access_key_id='YYYY'  Rds stop
```

