# cpmawscli
This script is intended for use via a scheduler like rundeck to automate shut downs and restarts of parts of an AWS infrastructure.
It has be designed in a modular way so that adding support for new AWS entity is done via adding files.

## Changelog

* 2016/03/15 
  * support for EC2 (stop start list)
  * support for RDS (stop start list)
  * filter by tags values (in an AND way not OR) or filter by instance name
  * exclude instances by name
  * use [boto3](https://github.com/boto/boto3) waiters

```
usage: cpmawscli.py [-h] (--tag key value | --instance INSTANCE) [--dryrun]
                    [--exclude [EXCLUDE [EXCLUDE ...]]]
                    [--loglevel {debug,info,notice,warning,error,critical}]
                    [--aws_access_key_id AWS_ACCESS_KEY_ID]
                    [--aws_secret_access_key AWS_SECRET_ACCESS_KEY]
                    {Ec2,Rds} ...
```

## Example :
stop all rds instances with tag Env=integ except instance foo and instance bar
```
./cpmawscli.py  --tag Env integ --except foo bar --aws_secret_access_key='xxxxxx' --aws_access_key_id='YYYY'  Rds stop
```

## Code structure
* directory core : main classes shouldn't be modified to add plugin 
* directory classes : classes and collections for AWS entities, files can be added to support new entities
* directory plugin : classes corresponding to manipulation of a specific amazon entity. Class methods are action on those entities via command line.

## Aws authentication
* either via --aws_access_key_id and --aws_secret_access_key or put your credentials in ~/.aws
