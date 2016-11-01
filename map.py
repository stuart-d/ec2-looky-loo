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

    def printout(self,label="default"):
        payload = ""
        for key, data in enumerate(self.index[label]):
            payload = payload + data
        soup = BeautifulSoup(payload, 'html.parser')
        return(soup.prettify())

def lambda_handler(event,context):
    client = boto3.client('ec2')
    vpcs = client.describe_vpcs()

    output = HtmlDoc()
    output.add('<html>')
    for vpc in vpcs['Vpcs']:
        output.add('<div class="vpc">')
        line = str(vpc['VpcId']) + "<br>"
        output.add(line)
        output.add("</div>")
    #output.add_table(["data",'data1'])
    output.add("</html>")
    output.print_labels()
    print(output.printout())
    return(output.printout())
    #output.set_label("default")
    #print output.printout(label="stuart")
