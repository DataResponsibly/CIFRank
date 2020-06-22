#!/bin/bash
#################################################
#						#
# Properties for complete routine		#
#						#
#################################################
#################################################
#						#
# Functions for complete routine		#
#						#
#################################################
function writeInfoFile {
	# $1 is ranker name
	# $2...n are hyper parameters for training
	
	infofile="$dataRootPath/ranklib-experiments/$1/training-parameters-info.txt"
	case "$1" in
		#writing infofile to evaluate quality of training parameters
		"MART" | "LambdaMART" )
		if [ -e $infofile ]; then
  		  echo "$2; $3; $4;" >> $infofile
		else
		  echo "MART PARAMETERS WITH MAP EVALUATION" > $infofile
		  echo "Shrinkage; Trees; Leafs; MAP; NDCG" >> $infofile
  	  	  echo "$2; $3; $4;" >> $infofile
		fi;;
		"ListNet" )
		if [ -e $infofile ]; then
                  echo "$2; $3;" >> $infofile
		else
		  echo "LISTNET PARAMETERS WITH MAP EVALUATION" > $infofile
		  echo "Learning Rate; Epochs; MAP; NDCG" >> $infofile
  	  	  echo "$2; $3;" >> $infofile
		fi;;
		"CoordinateAscent" )
		if [ -e $infofile ]; then
                  echo "$2; $3; $4;" >> $infofile
		else
		  echo "COORDINATE ASCENT PARAMETERS WITH MAP EVALUATION" > $infofile
		  echo "Random Restarts; Iteration; Performance Tolerance; MAP; NDCG" >> $infofile
  	  	  echo "$2; $3; $4;" >> $infofile
		fi;;
	esac
}
function createDirs {
	mkdir $1
	mkdir $1/models
	mkdir $1/predictions
}

function runRanker {
	# first argument experiment directory, 
	# second argument ranker name, 
	# third ranker number, 
	# fourth timestamp in training data files
	# last n arguments are hyper parameters for individual rankers
	echo " "
	echo "########################################"
	echo " "
	echo "Start training with ranker $2 using file $4"
	echo " "
	echo "########################################"
	
	case "$2" in
		"MART" | "LambdaMART" )
		if [ "$#" -ne 7 ]; then echo "ERROR: incorrect number of arguments for MART or LambdaMART"; exit -1; fi
		java -jar $RANK_LIB_FILE -train $dataRootPath/$4_train_ranklib.txt \
			-ranker $3 -shrinkage $5 -tree $6 -leaf $7 -gmax $RELEVANCE_LABEL \
			-metric2t $EVAL_M -metric2T $EVAL_M -save $1/models/$4_model.txt;;
		"ListNet" )
		if [ "$#" -ne 6 ]; then echo "ERROR: incorrect number of arguments for ListNet"; exit -1; fi
		java -jar $RANK_LIB_FILE -train $dataRootPath/$4_train_ranklib.txt \
			-ranker $3 -lr 0.000001 -epoch $6 -gmax $RELEVANCE_LABEL \
			-metric2t $EVAL_M -metric2T $EVAL_M -save $1/models/$4_model.txt;;
		"CoordinateAscent" )
		if [ "$#" -ne 7 ]; then echo "ERROR: incorrect number of arguments for CoordinateAscent"; exit -1; fi
		java -jar $RANK_LIB_FILE -train $dataRootPath/$4_train_ranklib.txt \
			-ranker $3 -r $5 -i $6 -tolerance $7 -gmax $RELEVANCE_LABEL \
			-metric2t $EVAL_M -metric2T $EVAL_M -save $1/models/$4_model.txt;;
		* )
		# anything else
		if [ "$#" -ne 4 ]; then exit -1; fi
		java -jar $RANK_LIB_FILE -train $dataRootPath/$4_train_ranklib.txt -ranker $3 -gmax $RELEVANCE_LABEL \
			-metric2t $EVAL_M -metric2T $EVAL_M -save $1/models/$4_model.txt;;
	esac
	
	echo " "	
	echo "########################################"
	echo " "
	echo "Predicting scores for ranker $2 using file $4"
	echo " "
	echo "########################################"
	java -jar $RANK_LIB_FILE -load $1/models/$4_model.txt -rank $dataRootPath/$4_test_ranklib.txt \
		-indri $1/predictions/prediction.txt
	
	
}

function startExperiment {
	if [ ! -d "$1" ]; then
		createDirs "$1"
	fi
	runRanker $1 $2 $3 $4 ${@:5}
}


#################################################
#						#
# Start of the complete routine			#
#			                        #
#################################################

LTR_SRC_DIR=$1
RANK_LIB_FILE="$LTR_SRC_DIR/RankLib-2.12.jar"
METRIC="$2" 	#"ERR@50"		#"MAP"
RELEVANCE_LABEL=$3  # set number of relevance labels

ranker="$4"				# read name of ranker from terminal
rankerID=$5				# read ranker ID from terminal
dataRootPath="$6"			# path to experimental dataset

EVAL_M="$METRIC@$RELEVANCE_LABEL"
# THE LAST N ARGUMENTS OF THIS SCRIPT WILL BE HYPER PARAMETERS FOR TRAINING. 
# THEIR NUMBER CAN NOT BE SPECIFIED BEFORE RUNTIME BECAUSE DIFFERENT RANKERS NEED DIFFERENT PARAMETERS
# HENCE WE LOOP OVER ALL ARGUMENTS UNTIL WE COLLECTED THEM ALL

hyperParameters="${@:7}"

#for ((i=4;i<=$#;i++)); do echo "$#" "$i" "${!i}"; done

if [[ $dataRootPath == */ ]]; then
	dataRootPath="${dataRootPath::-1}"
fi

# write file about current training configuration
# writeInfoFile $ranker $hyperParameters

dateAndTime="experiments_$(date +%Y%m%d_%H%M%S)"

if true; then 
for trainingfile in `find $dataRootPath -type f -regex '.*[A-Za-z0-9]*\_train\_ranklib\.txt'`; do
	trainingfile=$(basename $trainingfile)
    
    	timestamp=${trainingfile%"_train_ranklib.txt"}
    
    	# create new experiments dir
	exp_dir="$dataRootPath/ranklib-experiments/$ranker/$dateAndTime/$timestamp"
	if [ ! -d "$exp_dir" ]; then
		echo "New experiments dir created."
	 	mkdir -p $exp_dir
		mkdir $exp_dir/models
		mkdir $exp_dir/predictions
	fi

	# create info file
	infofile="$exp_dir/info.txt"
	echo $exp_dir
	if [ -e $infofile ]; then
		echo "File $infofile already exists!"
	else
		echo "Experiments properties " > $infofile
		echo "Ranker $ranker" >> $infofile
		echo "Ranker Parameters $hyperParameters" >> $infofile
		echo "Executed $(date +%d%m%Y) " >> $infofile
		echo "Relevance labels range: $RELEVANCE_LABEL" >> $infofile
		echo "Metric: $EVAL_M" >> $infofile
	fi

    	# start experiments and exit whole script if function returns -1
	set -e 
	startExperiment $exp_dir $ranker $rankerID $timestamp $hyperParameters
	set +e	
done
fi
