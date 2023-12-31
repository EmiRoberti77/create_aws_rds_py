import boto3
rds_client = boto3.client('rds')
""":type pyboto3.rds"""

RDS_DB_SUBNET_GROUP = "emi-rds-subnet-group"

def create_db_subnet_group():
  print("creating rds subnet group")
  subnetIds = ['subnet1', 
               'subnet2', 
               'subnet']
  rds_client.create_db_subnet_group(
    DBSubnetGroupName=RDS_DB_SUBNET_GROUP,
    DBSubnetGroupDescription="emi subnet group",
    SubnetIds=subnetIds
  )

def create_db_security_group_and_add_inbound_rule():
  ec2 = boto3.client('ec2', region_name="us-east-1")
  """ :type : pyboto3.ec2 """

  # create security group
  security_group = ec2.create_security_group(
      GroupName="emi-rds-pub-sg",
      Description="RDS security group to allow public access",
      VpcId="vpc-id"
  )

  # get id of the
  security_group_id = security_group['GroupId']
  print("created RDS security groupId", security_group_id)

  # add public access rule to sg
  ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

  print("Added inbound access rule to security group with id " + security_group_id)
  return security_group_id

def launch_rds_instance():
    print("Launching AWS RDS PostgreSQL instance...")

    security_group_id = create_db_security_group_and_add_inbound_rule()

    create_db_subnet_group()
    print("Created DB Subnet Group")

    rds_client.create_db_instance(
        DBName='PostgreSQLDBInstance',
        DBInstanceIdentifier="postgresqlinstanceidentifier",
        DBInstanceClass="db.t2.micro",
        Engine="postgres",
        EngineVersion="15.2",
        Port=5432,
        MasterUsername="postgres",
        MasterUserPassword="mypostgrespassword",
        AllocatedStorage=20,
        MultiAZ=False,
        StorageType="gp2",
        PubliclyAccessible=True,
        VpcSecurityGroupIds=[security_group_id],
        DBSubnetGroupName=RDS_DB_SUBNET_GROUP
    )


if __name__ == '__main__':
    print("launching RDS")
    launch_rds_instance()