
cfg.export_png = 'True'; %toggle png writing? 'False' or 'True';
cfg.export_fbx = 'False'; %toggle fbx writing? 'False' or 'True';
cfg.export_gltf = 'True'; %toggle gltf writing? 'False' or 'True';

cfg.blender_path = '/Applications/Blender.app/Contents/MacOS/Blender'; % Change this to the path to your Blender application
cfg.blender_file_path = '/Users/wenxuan/Documents/Blender/makeQuaddle.blend'; % Change this to your makeQuaddle file path
cfg.python_script = '/Users/wenxuan/Documents/Blender/parser.py'; % Change this to your Python script path

cfg.num_quaddles = 4;
cfg.nVaryingDimensions = 17;
cfg.blender_input_path = [pwd '/CONFIG/'];
cfg.blender_output_path = [pwd '/TaskResources']; 
cfg.controlRandomnessMode0_controlFeaturesMode1 = 0;
cfg.ss_loBound = 8;
cfg.ss_upBound = 12;
cfg_out = make_Quaddles(cfg);
