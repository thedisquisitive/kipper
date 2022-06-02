export FLASK_APP=main
export FLASK_ENV=development

if flask -v &> /dev/null
then
    flask run
elif python3 -v &> /dev/null
    python3 -m flask run 
else
    python -m flask run 

