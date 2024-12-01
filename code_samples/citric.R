# start example
> library(reticulate)
> reticulate::use_virtualenv("venv")
> reticulate::source_python("export_ls_responses.py")
> py$survey_data
  submitdate lastpage startlanguage        seed     G01Q01 G01Q02 G02Q03 G02Q03[filecount]
1      [nan]      [1]        ['en'] [245240561] ['lalala']    [5]  [nan]             [nan]
# end example
