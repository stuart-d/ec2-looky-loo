from __future__ import print_function
import boto3
import re
from bs4 import BeautifulSoup

class HtmlDoc(object):
    def __init__(self):
        self.index = dict()
        self.set_label()

    def print_labels(self):
        for label in self.index.iterkeys():
            print (label)

    def set_label(self,label="default"):
        if label not in self.index:
            self.index[label] = []
        self.label = label

    def add_table(self,content,type="row",style=""):
        label = self.label
        if not isinstance(content,list):
            return("error: not a list")

        element_open_tag = "<td class=" + style + ">"
        element_close_tag = "</td>"
        if type == "header":
            element_open_tag = "<th class=" + style + ">"
            element_close_tag = "</th>"

        payload = "<tr>"
        for key, data in enumerate(content):
            payload = payload  + element_open_tag + data + element_close_tag
        payload = payload + "</tr>\n"
        self.index[label].append(payload)

    def add(self,content,type="line"):
        label = self.label
        if type == "line":
            content = content + "\n"
        self.index[label].append(content)

    def render(self,label="default"):
        payload = ""
        for key, data in enumerate(self.index[label]):
            payload = payload + data
        soup = BeautifulSoup(payload, 'html.parser')
        return(payload)
        #return(soup.prettify())

def lambda_handler(event,context,debug="false"):

    tool_name ="EC2-looky-loo"
    tool_location = "https://github.com/stuart-d/ec2-looky-loo"
    tool_version ="0.6"

    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    azs = client.describe_availability_zones()
    vpcs = client.describe_vpcs()
    subnets = client.describe_subnets()
    routetables = client.describe_route_tables()
    networkacls = client.describe_network_acls()

    output = HtmlDoc()

    output.add('<!DOCTYPE html>')
    output.add('<html>')
    output.add('<head> <link rel="stylesheet" type="text/css" href="https://sdevenis-lambda.s3.amazonaws.com/main.css"> </head>')
    output.add('<p style="tool_header">' + tool_name + '</p>')
    output.add('<p> Version: <a href="' + tool_location + '">' + tool_version + '</a></p>')

    for vpc in vpcs['Vpcs']:
        output.add("<div class=\"vpc\">")
        line = str(vpc['VpcId']) + "<br>"
        output.add(line)
        if 'Tags' in vpc.keys():
            output.add('<table class="tags">')
            for tag in vpc['Tags']:
                output.add_table([tag['Key'],tag['Value']],style="tags")
            output.add('</table>')

        for az in azs['AvailabilityZones']:
            az_name = str(az['ZoneName'])
            output.add("<div class=\"" + az_name + "\">")
            output.add("<p class=\"az_header\">Availability Zone: " + az_name + "</p>")

            for subnet in subnets['Subnets']:
                if subnet['VpcId'] == vpc['VpcId'] and subnet['AvailabilityZone'] == az_name:
                    output.add("<div class=\"subnet\">")
                    output.add("<p class=\"az_header\">" +  subnet['SubnetId'] + "  [" + subnet['CidrBlock'] + "]<br>")
                    print (subnet)
                    if 'Tags' in subnet.keys():
                        output.add('<table class="tags">')
                        for tag in subnet['Tags']:
                            output.add_table([tag['Key'],tag['Value']],style="tags")
                        output.add('</table>')


                    # Begin Route Tables
                    output.add("<p class=\"subnet_category_header\">Route Tables</p>")
                    for routetable in routetables['RouteTables']:
                        attached_route_table = ""
                        print (routetables)
                        for association in routetable['Associations']:

                            if "SubnetId" in association.keys() and association['SubnetId'] == subnet['SubnetId']:

                                attached_route_table = association['RouteTableId']

                                output.add(association['RouteTableId'] + "<br>")
                                output.add('<table class="hosts">')
                                output.add_table(["Dest CIDR","GW"],type="header")

                                for route in routetable['Routes']:
                                    gw = "-"
                                    if "GatewayId" in route.keys():
                                        gw = route['GatewayId']
                                    if "NatGatewayId" in route.keys():
                                        gw = route['NatGatewayId']
                                    output.add_table([route['DestinationCidrBlock'],gw])
                                output.add('</table>')

                    # Begin Network ACLs
                    output.add("<p class=\"subnet_category_header\">Network ACLs</p>")
                    for networkacl in networkacls['NetworkAcls']:
                        for aclassociation in networkacl['Associations']:
                            if aclassociation['SubnetId'] == subnet['SubnetId']:
                                output.add(networkacl['NetworkAclId'])
                                output.add("<table class=\"hosts\">")
                                output.add_table(['Rule','Protocol','Ports','RuleAction','Egress','CidrBlock'],type="header")

                                for entry in networkacl['Entries']:
                                  rule_number = str(entry['RuleNumber'])
                                  rule_action = str(entry['RuleAction'])
                                  cidr = str(entry['CidrBlock'])

                                  port_range = "all"
                                  if 'PortRange' in entry:
                                      ports_from = str(entry['PortRange']['From'])
                                      ports_to = str(entry['PortRange']['To'])
                                      port_range = ports_from + "-" + ports_to

                                  direction = "ingress"
                                  if entry['Egress'] == True:
                                      direction == "egress"
                                      protocol = entry['Protocol']
                                      protocol = re.sub("-1","all",protocol)
                                      protocol = re.sub("6","tcp",protocol)
                                      output.add_table([rule_number,protocol,port_range,rule_action,direction,cidr])
                                output.add("</table>")


                    # Begin EC2 instaces
                    output.add("<p class=\"subnet_category_header\">EC2 Instances</p>")
                    output.add("<table class=\"hosts\">\n")
                    output.add_table(["Name","State","Type","Address","Security Groups","Platform"],type="header")
                    for i in instances:
                        for interface in i.network_interfaces_attribute:
                            if interface['SubnetId'] == subnet['SubnetId']:

                                name = "-"
                                for tag in i.tags:
                                    if tag['Key'] == 'Name':
                                        name = tag['Value']

                                state = i.state['Name']
                                instance_type = i.instance_type

                                address = interface['PrivateIpAddress']

                                groups = ""
                                for group in interface['Groups']:
                                    groups = groups + group['GroupId']

                                platform = "linux"
                                if i.platform:
                                    platform = i.platform

                                output.add_table([name,state,instance_type,address,groups,platform])
                    output.add("</table>")

                    output.add("</div><p>") # close Subnet div

            output.add("</div>") # close AvailabilityZone div

        output.add("</div>") # close VPC div

    output.add("</html>")

    body = output.render()
    if debug == "true":
        print (body)
    payload = { "statusCode": "200", "headers": {"Content-Type": "text/html"}, "body": body }
    return(payload)
