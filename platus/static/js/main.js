$(document).ready(function() {

    // Begin Projects
    $('#env_action_create').on('click', function() {
        if ($(this).is(':checked'))
            $('#env_action_delete').attr("disabled", true);
        else
            $('#env_action_delete').attr("disabled", false);
    });
    
    $('#env_action_delete').on('click', function() {
        if ($(this).is(':checked'))
            $('#env_action_create').attr("disabled", true);
        else
            $('#env_action_create').attr("disabled", false);
    });

    $('#project_create').on('click', function() {
        if ($(this).is(':checked'))
            $('#project_delete').attr("disabled", true);
        else
            $('#project_delete').attr("disabled", false);
    });
    
    $('#project_delete').on('click', function() {
        if ($(this).is(':checked'))
            $('#project_create').attr("disabled", true);
        else
            $('#project_create').attr("disabled", false);
    });

    $("#project_group option").each(function(){
        if ($(this).val() === "grpuppet")
            $(this).prop('selected', 'selected').change();
    });
    // End Projects

    // Begin Users Env
    $('#add_projects').on('click', function() {
        $("#projects").toggle();
    });

    $('#addMore').on('click', function() {
        var data = $("#tb_projects tr:eq(1)").clone(true).appendTo("#tb_projects");
        data.find("input").val('');
    });

    $('.remove_row').on('click', function() {
        var trIndex = $(this).closest("tr").index();
            if(trIndex>0) {
             $(this).closest("tr").remove();
        } else {
             alert("Sorry!! Can't remove first row!");
        }
    });

    $('#projects_group').change(function() {
        var row = $(this).parent().parent();
        var row_project_name = row.children().eq(1).children();
        var request_type = "projects";
        var path = $(this).val()
        $.ajax({
            url: '/data',
            type: 'GET',
            data: {
                    'type': request_type,
                    'path': path
            },
            dataType: 'json',
            success: function(data){
                        row_project_name.empty();
                        row_project_name.append( new Option("None", "") )
                        $.each(data,function(index,value){
                            row_project_name.append( new Option(value, value) )
                        });
            }
        });
    });

    $('#project_name').change(function() {
        var row = $(this).parent().parent();
        var row_project_group = row.children().eq(0).children();
        var row_project_branch = row.children().eq(3).children();
        var request_type = "project_branches";
        var path = row_project_group.val() + "/" + $(this).val()
        $.ajax({
            url: '/data',
            type: 'GET',
            data: {
                    'type': request_type,
                    'path': path
            },
            dataType: 'json',
            success: function(data){
                        row_project_branch.empty();
                        row_project_branch.append( new Option("None", "") )
                        $.each(data,function(index,value){
                            row_project_branch.append( new Option(value, value) )
                        });
            }
        });
    });

    $("#myform").submit(function(e) {
        e.preventDefault();
        var actionurl = e.currentTarget.action;
        var tb_projects = $('#tb_projects').tableToJSON({
            ignoreColumns : [4],
            textExtractor : function(cellIndex, $cell) {
                  return $cell.find('select').val();
            }
        });
        var tb_def_projects = $('#tb_def_projects').tableToJSON({
            textExtractor : function(cellIndex, $cell) {
                  return $cell.find('input').val();
            }
        });
        var table = $.merge(tb_def_projects, tb_projects);
        var projects = JSON.stringify(table);
        var data = $(this).serialize()+'&'+$.param({projects});

        $.ajax({
            type: 'post',
            url: actionurl,
            data: data,
            success : function(data){
                $("#result").html(data);
                $("#reset").trigger("click");
            },
            error: function(jqXHR,error, errorThrown) {  
                if(jqXHR.status&&jqXHR.status==400){
                    alert(jqXHR.responseText); 
                }else{
                   alert("Something went wrong");
                }
            },
            complete: function(){
                $('#loading-bk').css('display', 'none');
                $('#loading').css('display', 'none');
            }
        });
    });

    var jsonDefaultEnv =
    [
        {
            "group" : "grpuppet",
            "name"  : "site-profiles",
            "access": "30",
            "branch": "development"
        },
        {
            "group" : "grpuppet",
            "name"  : "r10k-main",
            "access": "",
            "branch": "development"
        }
    ];

    $('#tb_def_projects').mounTable(jsonDefaultEnv);
    // Begin Users Env

    $('#submit').on('click', function() {
        $('#loading-bk').css('display', 'block');
        $('#loading').css('display', 'block');
    });
});

