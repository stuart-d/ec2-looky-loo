from __future__ import print_function
import boto3
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

        element_open_tag = "<td>"
        element_close_tag = "</td>"
        if type == "header":
            element_open_tag = "<th>"
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
    client = boto3.client('ec2')
    azs = client.describe_availability_zones()
    vpcs = client.describe_vpcs()
    subnets = client.describe_subnets()
    routetables = client.describe_route_tables()

    output = HtmlDoc()
    output.add('<!DOCTYPE html>')
    output.add('<html>')
    output.add('<head> <link rel="stylesheet" type="text/css" href="https://sdevenis-lambda.s3.amazonaws.com/main.css"> </head>')

    for vpc in vpcs['Vpcs']:
        output.add("<div class=\"vpc\">")
        line = str(vpc['VpcId']) + "<br>"
        output.add(line)

        for az in azs['AvailabilityZones']:
            az_name = str(az['ZoneName'])
            output.add("<div class=\"" + az_name + "\">")
            output.add("<p class=\"az_header\">Availability Zone: " + az_name + "</p>")

            for subnet in subnets['Subnets']:
                if subnet['VpcId'] == vpc['VpcId'] and subnet['AvailabilityZone'] == az_name:
                    output.add("<div class=\"subnet\">")
                    output.add("<p class=\"az_header\">" +  subnet['CidrBlock'] + "  [" + subnet['SubnetId'] + "]<br>")

                    for routetable in routetables['RouteTables']:

                        for association in routetable['Associations']:

                            if "SubnetId" in association.keys() and association['SubnetId'] == subnet['SubnetId']:
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

                    output.add("</div>")

            output.add("</div>")

        output.add("</div>")

    output.add("</html>")

    body = output.render()
    if debug == "true":
        print (body)
    payload = { "statusCode": "200", "headers": {"Content-Type": "text/html"}, "body": body }
    return(payload)
