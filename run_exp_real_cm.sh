#!/bin/bash
############################
#						   #
# default setting for LTR  #
#						   #
############################

LTR_DATA_DIR=out/ranklib_data
LTR_SRC_DIR=src/ranklib
LTR_RANKER=ListNet
LTR_RANKER_ID=7
LTR_OPT_METRIC=NDCG
LTR_OPT_K=500
LTR_LEARNING_RATE=0.000001
LTR_EPOCHS=10000


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
DATA_N=4162   
SRC_DATA="data/COMPAS" 
COUNT_FILE_NAME="_count"
SPLIT_FLAG=Yes
EVAL_K=500,1000,1500


LTR_TRIAL_N=10
DATA_TRIAL_N=1
LTR_SETTINGS=("Full")


DATA_FLAG=cm
MODEL_FLAG=m2
MEDIATOR_ATT=GR 


#########################################################
#						                                #
# Functions for estimate causal model on the data,      #
# causal model is specified in 'rscripts'               #
#						                                #
#########################################################
Rscript --vanilla "$R_SRC_DIR/${DATA_FLAG}_${MODEL_FLAG}.R" $R_DATA_DIR $SRC_DATA


############################################################################
#						                                                   #
# Functions to get counterfactual data from estimated causal model         #
#						                                                   #
############################################################################

COUNTER_G=FB
echo "MEDIATION ON TWO SENSITIVE ATTRIBUTES GENDER AND RACE"
python "$PY_SRC_DIR/gen_counter_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --src_data $SRC_DATA --counter_g $COUNTER_G --val_n $DATA_N --counter_run $DATA_TRIAL_N 


##############################################
#						                     #
# Functions to prepare ranklib inputs        #
# ONLY SUPPORT MODEL m1 and m2 NOW	         #
#						                     #
##############################################
if [ $MODEL_FLAG == "m2" ] 
then
	EVAL_COUNTER_RANKINGS="Y,Y_count,Y_count_resolve"
	EVAL_LTR_RANKINGS="Y__Y__full,Y_count__Y__full,Y_count__Y_count__full,Y_count_resolve__Y__full,Y_count_resolve__Y_count_resolve__full"
	echo "EVALUATION ON BOTH RESOLVING AND NON-RESOLVING"
else
	EVAL_COUNTER_RANKINGS="Y,Y_count"
	EVAL_LTR_RANKINGS="Y__Y__full,Y_count__Y__full,Y_count__Y_count__full"
	echo "EVALUATION ON NON-RESOLVING"
fi

# evaluation for selection rate for counterfactual
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $EVAL_K --rankings "$EVAL_COUNTER_RANKINGS,Y_quotas_R,Y_quotas_G,Y_quotas_GR" --measure select_rate --file_n $COUNT_FILE_NAME
# evaluation for rKL
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $EVAL_K --rankings $EVAL_COUNTER_RANKINGS --measure rKL --file_n $COUNT_FILE_NAME
# evaluation for ratio
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $EVAL_K --rankings $EVAL_COUNTER_RANKINGS --measure igf --file_n $COUNT_FILE_NAME
# evaluation for score utility
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $EVAL_K --rankings "$EVAL_COUNTER_RANKINGS,Y_quotas_R,Y_quotas_G,Y_quotas_GR" --measure score_utility --file_n $COUNT_FILE_NAME



##########################################
#						                 #
# Functions to prepare LTR DATA          #
# ONLY SUPPORT MODEL m1 and m2 NOW	     #
#						                 #
##########################################

python "$PY_SRC_DIR/gen_ranklib_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --opt_k_list "$LTR_OPT_K,$LTR_OPT_K" --total_n $DATA_N --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --test_input bias --train_input bias --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG
python "$PY_SRC_DIR/gen_ranklib_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --opt_k_list "$LTR_OPT_K,$LTR_OPT_K" --total_n $DATA_N --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --test_input bias --train_input fair_count --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG
python "$PY_SRC_DIR/gen_ranklib_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --opt_k_list "$LTR_OPT_K,$LTR_OPT_K" --total_n $DATA_N --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --test_input fair_count --train_input fair_count --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG
python "$PY_SRC_DIR/gen_ranklib_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --opt_k_list "$LTR_OPT_K,$LTR_OPT_K" --total_n $DATA_N --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --test_input bias --train_input fair_res --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG
python "$PY_SRC_DIR/gen_ranklib_data.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --opt_k_list "$LTR_OPT_K,$LTR_OPT_K" --total_n $DATA_N --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --test_input fair_res --train_input fair_res --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG


################################
#						       #
# Functions for LTR ranker	   #
#						       #
################################
for i in "${LTR_SETTINGS[*]}"
do
	echo " "	
	echo "#################### LTR ##################"
	echo " "

	bash "$LTR_SRC_DIR/run-LTR-model.sh" $LTR_SRC_DIR $LTR_OPT_METRIC $LTR_OPT_K $LTR_RANKER $LTR_RANKER_ID "$LTR_DATA_DIR/$DATA_FLAG/$MODEL_FLAG/$i/bias__bias" $LTR_LEARNING_RATE $LTR_EPOCHS
    bash "$LTR_SRC_DIR/run-LTR-model.sh" $LTR_SRC_DIR $LTR_OPT_METRIC $LTR_OPT_K $LTR_RANKER $LTR_RANKER_ID "$LTR_DATA_DIR/$DATA_FLAG/$MODEL_FLAG/$i/fair_count__bias" $LTR_LEARNING_RATE $LTR_EPOCHS
    bash "$LTR_SRC_DIR/run-LTR-model.sh" $LTR_SRC_DIR $LTR_OPT_METRIC $LTR_OPT_K $LTR_RANKER $LTR_RANKER_ID "$LTR_DATA_DIR/$DATA_FLAG/$MODEL_FLAG/$i/fair_count__fair_count" $LTR_LEARNING_RATE $LTR_EPOCHS
    bash "$LTR_SRC_DIR/run-LTR-model.sh" $LTR_SRC_DIR $LTR_OPT_METRIC $LTR_OPT_K $LTR_RANKER $LTR_RANKER_ID "$LTR_DATA_DIR/$DATA_FLAG/$MODEL_FLAG/$i/fair_res__bias" $LTR_LEARNING_RATE $LTR_EPOCHS
    bash "$LTR_SRC_DIR/run-LTR-model.sh" $LTR_SRC_DIR $LTR_OPT_METRIC $LTR_OPT_K $LTR_RANKER $LTR_RANKER_ID "$LTR_DATA_DIR/$DATA_FLAG/$MODEL_FLAG/$i/fair_res__fair_res" $LTR_LEARNING_RATE $LTR_EPOCHS
    

    echo "Finished all LTR train and test for setting $i."
    echo " "	
	echo "#################### LTR ##################"

done


#################################################################
#						                                        #
# Functions to get LTR prediction and evaluate on the test sets	#
#						                                        #
#################################################################

python "$PY_SRC_DIR/gen_LTR_pred.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --test_run $LTR_TRIAL_N --settings $LTR_SETTINGS --file_n $COUNT_FILE_NAME --split $SPLIT_FLAG

# LTR evaluation for selection rate
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $LTR_OPT_K --rankings $EVAL_LTR_RANKINGS --measure select_rate 

# LTR evaluation for sensitivity
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $LTR_OPT_K --rankings $EVAL_LTR_RANKINGS --measure sensitivity

# LTR evaluation for ap
python "$PY_SRC_DIR/eval_rankings.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --eval_ks $LTR_OPT_K --rankings $EVAL_LTR_RANKINGS --measure ap


#################################
#						        #
# Functions to generate plots 	#
#						        #
#################################

python "$PY_SRC_DIR/gen_plots.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --rankings $EVAL_COUNTER_RANKINGS --plot_ks $EVAL_K --y_col select_rate --y_max 2.2 --file_n $COUNT_FILE_NAME
python "$PY_SRC_DIR/gen_plots.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --rankings $EVAL_COUNTER_RANKINGS --plot_ks $EVAL_K --y_col rKL --y_max 6.1

python "$PY_SRC_DIR/gen_plots.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --rankings $EVAL_LTR_RANKINGS --opt_k $LTR_OPT_K --y_col select_rate --y_max 2 --file_n _LTR
python "$PY_SRC_DIR/gen_plots.py" --data_flag $DATA_FLAG --model_flag $MODEL_FLAG --rankings $EVAL_LTR_RANKINGS --opt_k $LTR_OPT_K --y_col sensitivity

