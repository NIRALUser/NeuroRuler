python cli.py --otsu data/IBIS_Case1_V06_t1w_RAI.nrrd
python cli.py --x=16 --y=2 --z=22 --slice=96 --otsu data/IBIS_Case1_V06_t1w_RAI.nrrd
python cli.py --slice=69 --lower=0.0 --upper=200.0 data/BCP_Dataset_2month_T1w.nrrd
python cli.py --otsu data/IBIS_Dataset_NotAligned_6month_T1w.nrrd
python cli.py --conductance=1.0 --iterations=20 --step=0.1 --otsu data/MicroBiome_1month_T1w.nii.gz