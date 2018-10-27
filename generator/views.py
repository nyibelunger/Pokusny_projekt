from datetime import datetime
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse
from django.urls import reverse
from .models import Question, Choice, User_input, Document
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.cache import cache, caches
import pandas as pd
from io import BytesIO
import xlsxwriter
import unicodedata

from django_pandas.managers import DataFrameManager
from .ais_file import generate_ais, Generate_for_all
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .forms import UploadFileForm, UploadDateForm,FormDateAndUpload


def home(request):

    def validate_input(date_input):
        valid = False
        try:
            date_input_year = int(date_input[:4])
            date_input_month = int(date_input[5:7])
            date_input_dict = {"month":date_input_month, "year":date_input_year}
            request.session["date_input_final"] = date_input_dict
            valid = True
        except ValueError:
            valid = False
        return valid, date_input_dict

    if request.method == 'POST':
        form = FormDateAndUpload(request.POST)
        print(request.POST.get('date', None))
        date_input = request.POST.get('date', None)

        #if form.is_valid():
        if validate_input(date_input):
            print("date input - %s" %date_input)
            print("validate")

            return render(request, 'ais_gen/input_excel.html')
    else:
        form = FormDateAndUpload()
        print("not valid")
    return render(request, 'ais_gen/home.html', {'form': form})

def upload_date(request):
    """view pro input data"""
    date_form = UploadDateForm(request.POST)
    return render(request, 'ais_gen/input_date.html', {'date_form': date_form})

def input_date(request):
    """
    grabne vložený datum a posuneho do input_excel()
    :param request:
    :return:
    """


    def validate_input(date_input):
        #global date_input_year, date_input_month
        valid = False
        try:
            date_input_year = int(date_input[:4])
            date_input_month = int(date_input[5:7])
            date_input_dict = {"month": date_input_month, "year": date_input_year}
            request.session["date_input_final"] = date_input_dict
            if date_input_year >= 2000 and date_input_year <= int(datetime.now().year) and date_input_month in range(1,13):
                valid = True
        except ValueError:
            valid = False
            raise ValidationError("Špatný formát datumu")
        return valid


    #date_input = request.POST.get('date', None)
    #date_input_year = int(date_input[:4])
    #date_input_month = int(date_input[5:7])

    #return render(request, 'ais_gen/input_excel.html')


    date_input = request.POST.get('date', None)

    if validate_input(date_input):
        print("valid - True")
        return render(request, 'ais_gen/input_excel.html')
    else:
        print("valid - False")
        messages.error(request, "Error")

def input_excel(request):
    #global user_select
    cele_datum = request.session["date_input_final"]
    if request.method == 'POST':
        print("cele_datum: %s" % cele_datum)
        date_input_month = cele_datum["month"]
        date_input_year = cele_datum["year"]
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['file'])
            novy_objekt = Generate_for_all(newdoc.docfile, date_input_year, date_input_month)
            user_select = novy_objekt.gen_ais_all()
            cache.set("user_select", user_select, 6000)
            print("cache: %s" %cache.get("user_select"))

            # Redirect to the document list after POST
            return render(request, 'ais_gen/user_selection.html', {'user_select':user_select})
        else:
            #form = DocumentForm()  # A empty, unbound form
            print("else:form - ok")
            return render(request, 'ais_gen/input_excel.html')

            # Load documents for the list page
        #documents = Document.objects.all()

        # Render list page with the documents and the form
        return render(request, 'ais_gen/input_excel.html')

def render_sel_us_ais(request):
    """
    view pro vygenerování xlsx souboru pro daného zaměstnance.
    :param request:
    :return:
    """
    uzivatel =  request.POST.get('zamestnanec', None)

    excel_file = BytesIO()
    #uzivatel_pd = user_select[uzivatel]
    uzivatel_pd = cache.get("user_select")[uzivatel]
    #uzivatel_pd = request.session['user_select'][uzivatel]
    #uzivatel_pd = request.session['user_select'][uzivatel]
    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    uzivatel_pd.to_excel(xlwriter, sheet_name='Sheet1')

    xlwriter.save()
    xlwriter.close()

    excel_file.seek(0)
    name = uzivatel

    filename = "ais" + "_" + uzivatel.split()[1] + "_" + str(request.session["date_input_final"]["year"]) + "_" + str(request.session["date_input_final"]["month"])
    normal_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('UTF-8').lower()

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # set the file name in the Content-Disposition header
    response['Content-Disposition'] = 'attachment; filename=%s.xlsx' %normal_filename

    return response


def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    return render(request, 'ais_gen/input_excel.html', {'form': form})


class IndexView(generic.ListView):
    template_name = 'ais_gen/index.html'
    context_object_name ='latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]



class DetailView(generic.DetailView):
    model = Question
    template_name = 'ais_gen/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that are not published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'ais_gen/results.html'


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'ais_gen/detail.html', {'question': question})



def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'ais_gen/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'ais_gen/detail.html',{
            'question':question, 'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('generator:results', args=(question.id,)))

def generator_ais(request):
    return HttpResponse("Vyberte požadovaný měsíc a vepište Vaše služby.")