FROM python:3.8
WORKDIR /app 
COPY /app/feature_imp_folder feature_imp_folder 
ADD /app/requirements.txt .
RUN pip install -r /app/requirements.txt
ADD /app/application_test.csv .
ADD /app/pipeline_transfo_model.pkl .
ADD /app/true_explainer.pkl .
EXPOSE 80
COPY ./ /app/
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]