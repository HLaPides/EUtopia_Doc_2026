# Individual Contributions

### Sidra Ansari

### Vineeth Kanpa

### Bennett LaPides

My primary contribution during phase 1 was idenitfying and evaluating data sources for our voter turnout and eu trust models. I pulled data from Eurostat and the World Bank and verified that their APIs were publically accessible and returning usable data. I also downloaded the 2024 Eurobaromter survey microdata from GESIS for our EU trust model. I also verified that the downloaded dataset could be read into python and properly parsed.

My primary contributions to phase 2 were data visualizations and an extensive EDA. I compiled the data gathered during phase 1 into two csvs for the two seperate models. The Eurostat and World Bank data was compiled into a dataset for voter turnout and the Eurobarometer survey was turned into a dataset for eu trust. I took the time to standardize the datasets, all 3 had different country codes, and clean the data to ensure that creating the ML models would go smoothly. The data visualizations and EDA helped us indentify important relationships like national turnout's relationship with eu turnout and satisfaction with democracy's relationship with EU trust. The analysis also helped us identify weaker relationships such as gender and eu trust. My work in phase 2 set us up to be successful with the ML models in phase 3.

For phase three I took Vineeth's proof of concept model from phase two and improved upon it. I switched it from a random forest to linear regression. I did extensive feature engineering. I added region as a field, added squared terms for median age and national turnount, a multiplyer between western europe and compulsory voting, and I tested many combinations of features to get the best model possible. I ended up with a LOO-CV r^2 of .79 and an RMSE of 8.8 %. I also created voter_turnout_diagnostics.py so that we could easily check assumptions for the model. Along with the diagnostics I created the backend model with predict() and test() functions that the routes would be able to call. 

For phase four most of my work was helping with EUtopia's frontend. I did a little on the backend, mainly moving the CSVS into the database and updating the schema so that the models could run smoothly. I started my work on the UI with the EU offical, I added the review lessons feature, the dashboard, and the voter turnout admin page. After I finisehd with that I moved on to the teacher persona where I created both tabs of the students page, the analytics page, and the create lessons functionality. I also updated the tables in the teacher according to feedback recieved during user testing. I also added a comparision table and heatmap to the country simulation.

### Meghan Paclob