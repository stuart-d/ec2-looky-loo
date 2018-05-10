from __future__ import print_function
import boto3
import re
import time
#from bs4 import BeautifulSoup

# This class provides a simple framework for structring the html output
# It maintains a index of label names, which can be appended to or rendedered
class HtmlDoc(object):
    def __init__(self):
        self.index = dict()
        self.set_label()

    # Print the curent labels (debugging)
    def print_labels(self):
        for label in self.index.iterkeys():
            print (label)

    # Set the label
    def set_label(self,label="default"):
        if label not in self.index:
            self.index[label] = []
        self.label = label

    # Bit of boilerplate for creating tables
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

    # Adds content to the current label
    def add(self,content,type="line"):
        label = self.label
        if type == "line":
            content = content + "\n"
        self.index[label].append(content)

    def render(self,label="default"):
        payload = ""
        for key, data in enumerate(self.index[label]):
            payload = payload + data
        #soup = BeautifulSoup(payload, 'html.parser')
        return(payload)
        #return(soup.prettify())

def lambda_handler(event,context,debug="false"):

    tool_name ="Application Infrastructure CNS AWS NonProd"
    tool_location = "https://github.com/stuart-d/ec2-looky-loo"
    tool_run_time = time.strftime("%d-%m-%Y %H:%M")

    # Need to have your profile configured in ~/.aws/config
    session = boto3.Session(profile_name='nonprod')

    client = session.client('ec2')
    azs = client.describe_availability_zones()
    vpcs = client.describe_vpcs()
    subnets = client.describe_subnets()
    routetables = client.describe_route_tables()
    networkacls = client.describe_network_acls()

    ec2 = session.resource('ec2')
    instances = ec2.instances.all()

    output = HtmlDoc()

    output.add('<!DOCTYPE html>')
    output.add('<html>')
    output.add('<head> <link rel="stylesheet" type="text/css" href="https://sdevenis-lambda.s3.amazonaws.com/main.css"> </head>')
    output.add('<p style="tool_header">' + tool_name + '</p>')
    output.add('<p> Generated: ' + tool_run_time + '</p>')

    for vpc in vpcs['Vpcs']:
        output.add("<div class=\"vpc\">")
        line = str(vpc['VpcId']) + "<br>"
        output.add(line)
        if 'Tags' in vpc.keys():
            output.add('<table class="tags">')
            for tag in sorted(vpc['Tags']):
                output.add_table([tag['Key'],tag['Value']],style="tags")
            output.add('</table>')

        for az in azs['AvailabilityZones']:
            az_name = str(az['ZoneName'])
            output.add("<div class=\"" + az_name + "\">")
            output.add("<p class=\"az_header\">Availability Zone: " + az_name + "</p>")

            for subnet in subnets['Subnets']:
                if subnet['VpcId'] == vpc['VpcId'] and subnet['AvailabilityZone'] == az_name:

                    # Check what classification this subnet is
                    subnet_class = "subnet"
                    zone = "unknown"
                    if 'Tags' in subnet.keys():
                        for tag in sorted(subnet['Tags']):
                            if tag['Key'] == "Zone2ZoneName":
                                zone =  tag['Value']
                                subnet_class = "subnet-" + zone


                    output.add("<div class=" + subnet_class + ">")
                    output.add("<p class=\"az_header\">" +  subnet['SubnetId'] + "  [" + subnet['CidrBlock'] + "]<br>")
                    if 'Tags' in subnet.keys():
                        output.add('<table class="tags">')
                        for tag in sorted(subnet['Tags']):
                            output.add_table([tag['Key'],tag['Value']],style="tags")
                        output.add("</table>")

                    # Begin Route Tables
                    output.add("<p class=\"subnet_category_header\">Route Tables</p>")

#                    print ("---")
#                    print (routetables)
#                    print ("---")
                    for routetable in routetables['RouteTables']:
                        for association in routetable['Associations']:
                            if "SubnetId" in association.keys() and association['SubnetId'] == subnet['SubnetId']:
                               attached_route_table = True
                               output.add(association['RouteTableId'] + "<br>")
                               output.add('<table class="hosts">')
                               output.add_table(["Destination","GW","Detail"],type="header")
                               for route in routetable['Routes']:
                                   gw = "-"
                                   destination = "-"
                                   detail = "-"
                                   if "GatewayId" in route.keys():
                                       gw = route['GatewayId']
                                   if "NatGatewayId" in route.keys():
                                       gw = route['NatGatewayId']
                                   if "DestinationCidrBlock" in route.keys():
                                       destination = route['DestinationCidrBlock']
                                   if "DestinationPrefixListId" in route.keys():
                                       destination = route['DestinationPrefixListId']
                                       r = client.describe_prefix_lists(PrefixListIds = [destination])
                                       detail = r['PrefixLists'][0]['PrefixListName']
                                       #print (r)

                                   output.add_table([destination,gw,detail])
                               output.add('</table>')

                    # Begin Network ACLs
                    output.add("<p class=\"subnet_category_header\">Network ACLs</p>")
                    for networkacl in networkacls['NetworkAcls']:
                        for aclassociation in networkacl['Associations']:
                            if aclassociation['SubnetId'] == subnet['SubnetId']:
                                output.add(networkacl['NetworkAclId'])
                                output.add("<table class=\"hosts\">")
                                output.add_table(['Rule','Protocol','Ports','RuleAction','Direction','CidrBlock'],type="header")

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
                                if i.tags:
                                    for tag in i.tags:
                                        if tag['Key'] == 'Name':
                                            name = tag['Value']

                                state = i.state['Name']
                                instance_type = i.instance_type

                                address = interface['PrivateIpAddress']

                                groups = ""
                                for group in interface['Groups']:
                                    groups = groups + "\n" + group['GroupId']

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
    #if debug == "true":
    #    print (body)
    payload = { "statusCode": "200", "headers": {"Content-Type": "text/html"}, "body": body }
    file = open("output.html","w")
    file.write(body)
    file.close()

    #return(payload)
