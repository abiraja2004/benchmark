# Create your views here.
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from libs.parser import Parser
from forms import ComparisonFilterForm
import os
import settings
import time
from plots.models import Md5Log, BenchmarkLogs, MachineInfo, RtAverage, RtMoss, RtBldg391, RtM35, RtSphflake, RtWorld, RtStar
from django.db import transaction

@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    transaction.commit()


def show_result(request, filename):
    #TODO: Check for the case when a duplicate file is submitted, with a pre-existing Md5 sum
    """
    """
    # Parse the file
    if not Md5Log.objects.filter(file_name=filename+'.log'):
        file = settings.MEDIA_ROOT + 'benchmarkLogs/' + filename + '.log'
        parser_obj = Parser(file)
        parser_obj.run()
    flush_transaction()
    #transaction.enter_transaction_management()
    #transaction.
    time.sleep(3)
    while not Md5Log.objects.filter(file_name=filename+'.log'):
        flush_transaction()
        print Md5Log.objects.filter(file_name=filename+'.log')
        flush_transaction()
        continue
    data_dict = {
    }
    #Query the database for Benchmark data from benchmark_logs table
    file_obj = Md5Log.objects.filter(file_name=filename+'.log')[0]
    data_dict['BRLCAD_Version'] = file_obj.benchmark.brlcad_version
    data_dict['Running_Time'] = file_obj.benchmark.running_time
    data_dict['Time_of_Execution'] = file_obj.benchmark.time_of_execution
    data_dict['VGR_Rating'] = file_obj.benchmark.approx_vgr
    data_dict['Log_VGR'] = file_obj.benchmark.log_vgr
    data_dict['Parameters'] = file_obj.benchmark.params

    #Query the database for System Information from machine_info table
    data_dict['Clock_Speed'] = file_obj.benchmark.machineinfo.cpu_mhz
    data_dict['NCores'] = file_obj.benchmark.machineinfo.cores
    data_dict['NProcessors'] = file_obj.benchmark.machineinfo.processors
    data_dict['Vendor_ID'] = file_obj.benchmark.machineinfo.vendor_id
    data_dict['OS_Type'] = file_obj.benchmark.machineinfo.ostype
    data_dict['Processor_Model_Name'] = file_obj.benchmark.machineinfo.model_name

    #Query the database for individual Image Performance
    data_dict['Rt_Average'] = file_obj.benchmark.rtaverage_set.all()[0].abs_rps
    data_dict['Rt_Bldg391'] = file_obj.benchmark.rtbldg391_set.all()[0].abs_rps
    data_dict['Rt_M35'] = file_obj.benchmark.rtm35_set.all()[0].abs_rps
    data_dict['Rt_Moss'] = file_obj.benchmark.rtmoss_set.all()[0].abs_rps
    data_dict['Rt_Sphlake'] = file_obj.benchmark.rtbldg391_set.all()[0].abs_rps
    data_dict['Rt_Star'] = file_obj.benchmark.rtstar_set.all()[0].abs_rps
    data_dict['Rt_World'] = file_obj.benchmark.rtworld_set.all()[0].abs_rps

    return render_to_response('result.html', data_dict, context_instance=RequestContext(request))


def compare_result(request, filename):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ComparisonFilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ComparisonFilterForm()

    return render(request, 'compare.html', {'form': form})



