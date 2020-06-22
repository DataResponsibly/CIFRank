#!/bin/bash


#########################
#						#
# default setting for R	#
#						#
#########################
R_DATA_DIR=out
R_SRC_DIR=src/rscripts


#################################
#						        #
# default setting for python	#
#						        #
#################################
PY_SRC_DIR=src/pyscripts
export PY_SRC_DIR="src/pyscripts"
export PY_DATA_SRC_DIR=data


###########################################################
#						                                  #
# INPUT SETTING for experiment, change based on dataset   #
#						                                  #
###########################################################
DATA_N=51   
SRC_DATA="data/CS" 
COUNT_FILE_NAME="_count"

DATA_TRIAL_N=1


DATA_FLAG=cs
MODEL_FLAG=m1
MEDIATOR_ATT=GR 


#########################################################
#						                                #
# Functions for estimate causal model on the data,      #
# causal model is specified in 'rscripts'               #
#						                                #
#########################################################
echo "MEDIATION ON TWO SENSITIVE ATTRIBUTES GENDER AND RACE"
Rscript --vanilla "$R_SRC_DIR/${DATA_FLAG}_${MODEL_FLAG}.R" $R_DATA_DIR $SRC_DATA


############################################################################
#						                                                   #
# Functions to get counterfactual data from estimated causal model         #
#						                                                   #
############################################################################

COUNTER_G=SS
python "$PY_SRC_DIR/gen_counter_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --src_data $SRC_DATA --counter_g $COUNTER_G --val_n $DATA_N --counter_run $DATA_TRIAL_N 


#################################
#						        #
# Functions to generate plots 	#
#						        #
#################################

python "$PY_SRC_DIR/gen_plots.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --rankings "Y,Y_count" --y_col rank --file_n $COUNT_FILE_NAME

