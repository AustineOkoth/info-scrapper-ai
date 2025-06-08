from django.shortcuts import render, redirect

# Import User
from django.contrib.auth.models import User


#Importing the django login authentifications
from django.contrib.auth import login , logout
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Iportant to serialize your data to a form understandable by rest frameworks.
#from .serlializers import NoteSerializer
from rest_framework import serializers

# Codes for rest_framework installation
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.http import HttpResponse

from openai import OpenAI
import os


class DummySerializer(serializers.Serializer):
    #I will add some data later on...
    pass

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
                
                print(company_name, company_url, company_location)   

                # Validate inputs
                if not all([company_name, company_url, company_location]):
                    print("Not all Colors Are Provided")
                    context.update({
                        'error': 'Please provide company name, URL, and location',
                        'result_color': 'red',
                    })
                    return render(request, 'index.html', context)

                # Initialize OpenAI client
                try:
                    client = OpenAI(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        timeout=120
                    )
                    print("API Keys are correctly set")
                    
                    
                except Exception as e:
                    
                    print("Failed to initialize OpenAI client:")
                    context.update({
                        'error': f"Failed to initialize OpenAI client: {str(e)}",
                        'result_color': 'red',
                    })
                    return render(request, 'index.html', context)

                # Build and send query
                try:
                    prompt = self.build_prompt(company_name, company_url, company_location)
                    
                    print(f"Prompt: {prompt}")
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
                    
                    print(f"Analysis failed: {str(e)}")
                    
                    context.update({
                        'error': f"Analysis failed: {str(e)}",
                        'result_color': 'red',
                    })

        return render(request, 'index.html', context)
        
        
    def build_prompt(self, company_name, company_url, company_location):
        return f"""
            TASK:
            Analyze the following company information and provide a detailed report:
            - Company Name: {company_name}
            - Company URL: {company_url}
            - Company Location: {company_location}

            INSTRUCTIONS:
            1. Search for any publicly available information about this company
            2. Verify if the name, URL, and location match known records
            3. Check for any inconsistencies or red flags
            4. Provide a summary of your findings

            FORMAT:
            - Start with "FINDINGS:" followed by your analysis
            - Clearly indicate if you found matching information, no information, or conflicting information
            - Be concise but thorough

            NOTE: If no information can be found, respond with "No relevant information found."
            """

    def determine_result_color(self, analysis_result):
            """Determine the color code based on the analysis result content"""
            analysis_result = analysis_result.lower()
            
            if "no relevant information found" in analysis_result:
                return "red"
            elif "conflict" in analysis_result or "inconsist" in analysis_result:
                return "yellow"
            elif "multiple" in analysis_result or "several" in analysis_result:
                return "grey"
            else:
                return "green"

                    
                    
                    
                    
                    
                    
                    
            
            
        #     def build_query(self, company_name, company_url, company_location):
            
        #         if company_name and company_url and company_location:
                    
        #                     return f"""
        #                     TASK:
        #                     You are analyzing the following information about a company:
        #                     - Company Name: {company_name}
        #                     - Company URL: {company_url}
        #                     - Company Location: {company_location}
                            
        #                     RULES:
                            
        #                     Return Any relevant information that can be found related to the company name, URL, and location.

        #                     """ 
        #                     #JUSTIFICATION: Provide a direct quote from Section {question.split(' ')[0]}, and explain your score using the results from factor validation, coverage verification, and the rules above. If no relevant content is found, respond with: "No relevant information found."
                                        
                    
        #     def _analyze_data(self, company_name, company_url, company_location):
        #                     """Core analysis logic shared by all assessment types."""
        #                     try:
        #                         if not company_name and company_url and company_location:
        #                             return print("Please provide a valid company name, URL, and location.")
                                    
        #                         try:
        #                             #vector_store = self.build_vector_store(text)
        #                             #retriever = vector_store.as_retriever(
        #                         #     search_kwargs={"k": 3, "score_threshold": 0.5}
        #                         # )
                                    
        #                             # qa = RetrievalQA.from_chain_type(
        #                             #     llm=self.llm,
        #                             #     chain_type="stuff",
        #                             #     retriever=retriever,
        #                             #     return_source_documents=True
        #                             # )
                                    
        #                             # qa = RetrievalQA.from_chain_type(
        #                             #     model_name="gpt-4",  # Or "gpt-3.5-turbo"
        #                             #     llm=self.llm,
        #                             #     chain_type="refine",  # or "map_reduce"
        #                             #     retriever=retriever,
        #                             #     return_source_documents=True
        #                             # )
                                    
        #                             print("I will update")
                                    
        #                         except Exception as e:
                                    
        #                             return print("I will update")
        #                             #return self._empty_response(frameworks, f"Initialization failed: {str(e)}", max_score, score_key)

        #                         results = {}
                
        #                         try:
        #                                 query = self.build_query(company_name, company_url, company_location)
        #                                 #response = qa.invoke({"query": query})
            
                        
                                        
        #                         except Exception as e:
        #                                 results = {
        #                                     'error': str(e),
        #                                     'response': 'Analysis failed',
        #                                     'score': 0
        #                                 }

                        


        #                     except Exception as e:
        #                         return {print(f"An error occurred: {str(e)}")}
                        
                                
                                
                    
                    
                    
                    
                    
                    
        #             # You can process the data here or save it to the database
            
            
        #     return render(request, 'index.html', {
        #                 'company_name': company_name,
        #                 'company_url': company_url,
        #                 'company_location': company_location,
        #                 'results': results,
        #             })
            
        # return render(request, 'index.html')

         
         
         
                
class InfoScrapperViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = DummySerializer
    
    
    @action(detail=False, methods=['get', 'POST'], url_path='analyze')
    def analyze(self, request):
        
        company_name = request.POST.get('companyName', None)
        company_url = request.POST.get('CompanywebUrl', None)
        company_location = request.POST.get('CompanyLocation', None)
        
        print(f"Company Name: {company_name}")
        print(f"Company URL: {company_url}")    
        print(f"Company Logo: {company_location}") 
        
        
        return render(request, 'index.html')
     
  