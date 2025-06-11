# Important to serialize your data to a form understandable by rest frameworks.
from rest_framework import serializers
from django.shortcuts import render

# Codes for rest_framework installation
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from openai import OpenAI
import os

import requests
import json

#NB: Make sure to install the required packages:
# pip install openai requests djangorestframework
#Make sure you have set the OPENAI_API_KEY in your environment variables.


class DummySerializer(serializers.Serializer):
    #I will add some data later on...
    pass

client = OpenAI( api_key=os.getenv("OPENAI_API_KEY"),timeout=200 )

class InfoScrapperDefaultPage(viewsets.ModelViewSet): 
      
    @action(detail=False, methods=['get', 'POST'], url_path='home')
    def default_page(self, request, *args, **kwargs):
        base_domain = request.build_absolute_uri('/')
        results = False
        
        # Initialize variables
        context = {
            'company_name': '',
            'company_url': '',
            'company_location': '',
            'results': False,
            'analysis_result': None,
            'result_color': '',
        }
            
        
        if request.method == 'POST':
                # Get form data
                company_name = request.POST.get('companyName', '').strip()
                company_url = request.POST.get('CompanywebUrl', '').strip()
                company_location = request.POST.get('CompanyLocation', '').strip()
                
                response_text = {}

                # Validate inputs, ensure all fields from form  are provided.
                if not all([company_name, company_url, company_location]):
                    print("Not all Colors Are Provided")
                    context.update({
                        'error': 'Please provide company name, URL, and location',
                        'result_color': 'red',
                    })
                    return render(request, 'index.html', context)

                # Initialize OpenAI client and Serper API
                try:

                    url = "https://google.serper.dev/search"

                    payload = json.dumps({
                    "q": f"{company_name} was founded in which year and its headquarters",
                    })
                    headers = {
                    'X-API-KEY': 'replace_with_your_serper_api_key',
                    'Content-Type': 'application/json'
                    }
                    response_text = requests.request("POST", url, headers=headers, data=payload)
                    
                    print(response_text.text)
                    
                    prompt = self.build_prompt(response_text.text, company_name, company_url, company_location)
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        max_tokens=2000
                    )
                    
                    analysis_result = response.choices[0].message.content
                    result_color = self.determine_result_color(analysis_result)
                    
                    
                    print(f"Analysis Result: {analysis_result}")
                    print(f"Result Color: {result_color}")

                    context.update({
                        'company_name': company_name,
                        'company_url': company_url,
                        'company_location': company_location,
                        'results': True,
                        'analysis_result': analysis_result,
                        'result_color': result_color,
                    })
                           
                except Exception as e:
                    
                    print(f"Failed : {e}")
                    context.update({
                        'error': f"Failed to initialize OpenAI client: {str(e)}",
                        'result_color': 'red',
                    })
                    return render(request, 'index.html', context)

        return render(request, 'index.html', context)    
        
    def build_prompt(self, response_text, company_name, company_url, company_location):    
        return f"""
    
           Your task is to analyze the information provided {company_name}, {company_url} and {company_location}. check whether the information provided is accurate or not. If headquarters and year founded for {company_name} is provided then state it. IF you don't have access to online information, then use {response_text} as the data that you need to analyze, if headquarters and year founded are not available, say "Headquarter and Year founded NOT available". Confirm whether the {company_name}, {company_url} and {company_location} (optional) from the data. 
            If you find information provided is accurate the return green, if you find conflicting information return yellow.. if you find no information at all return red. If you find multiple information return grey.
            """

    def determine_result_color(self, analysis_result):   
            """Determine the color code based on the analysis result content"""
            analysis_result = analysis_result.lower()
            
            if "red" in analysis_result:
                return "red"
            elif "yellow" in analysis_result or "green" and "red" in analysis_result:
                return "yellow"
            elif "grey" in analysis_result in analysis_result:
                return "grey"
            else:
                return "green"

                

     
  