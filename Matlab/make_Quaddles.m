function cfg_out = make_Quaddles2_03(cfg)

% cfg = [];

%  --- --- --- --- --- --- --- --- --- --- 
%  --- CONFIGURATION VARIABLES - change as desired: 
%  --- --- --- --- --- --- --- --- --- --- 


% if cfg.nVaryingDimensions > 15
%     cfg.controlRandomnessMode0_controlFeaturesMode1 = 0;
% else
%     cfg.controlRandomnessMode0_controlFeaturesMode1 = 1;
% end

if cfg.nVaryingDimensions < 1 || cfg.nVaryingDimensions > 17
    error('nVaryingDimensions set to a value out of range');
end

cfg_out = [];
cfg_out.objectTables      = {};
cfg_out.objectFileNames   = {};
cfg_out.objectFileFolders = {};
cfg_out.samples = {};

if ~exist(cfg.blender_input_path), mkdir(cfg.blender_input_path), end
if ~exist(cfg.output_path), mkdir(cfg.output_path), end
stim_iPath = cfg.blender_input_path;

gltf_files = struct('name', {}, 'idx', {}); % Initialize struct for stimdef writing

% creating list 'samples', which contains dimensions of an object
[dimension_name, dimension_value, available_dimensions] = init_dimensions(cfg.controlRandomnessMode0_controlFeaturesMode1, cfg.nVaryingDimensions);

possible_quaddles = 1;
% Loop through each dimension in available_dimensions
for i = 1:length(available_dimensions)
    % Get the current dimension name
    current_dimension = available_dimensions{i};
    
    % Get the corresponding value from the dimension_value dictionary
    value = dimension_value(current_dimension);
    
    % Multiply the current product by the value
    possible_quaddles = possible_quaddles * value;
end

if possible_quaddles < cfg.num_quaddles
    error(['The number of possible quaddles you can generate (', num2str(possible_quaddles), ') is less than the number of quaddles you are generating (', num2str(cfg.num_quaddles), ').']);
end

all_samples = zeros(cfg.num_quaddles, numel(dimension_name));

objectNames = {};

% Loop to create multiple samples (quaddles)
for q = 1:cfg.num_quaddles
    samples = cell(numel(dimension_name),1);
    % Loop over each dimension
    if cfg.controlRandomnessMode0_controlFeaturesMode1 == 0
        for i = 1:numel(dimension_name)
            % Set the number of samples to take from each dimension
            num_samples = dimension_value(dimension_name(i));
            % Randomly sample numbers: if it is in an available dimension, then randomly sample one of it
            if ismember(dimension_name(i), available_dimensions)
                samples{i} = randi(num_samples + 1, 1) - 1; % randomly sample one of the available options
            else
                samples{i} = 0; % assign 0 if the dimension is not available
            end
        end
        samples = cell2mat(samples);
        samples = samples';
        for i = 1:length(samples(:,1))
            samples(i,:) = modify_list(samples(i,:));
        end
        disp('*************FIRST SAMPLE HERE*************');
        disp(samples);
    end
    
    
%     if cfg.nVaryingDimensions == 16
%         ss_loBound = 6.5;
%         ss_upBound = 8;
%     elseif cfg.nVaryingDimensions == 17
%         ss_loBound = 9.25;
%         ss_upBound = 13.0;
%     end
	ss_loBound = cfg.ss_loBound;
	ss_upBound = cfg.ss_upBound;


    if all(all_samples(1,:) == 0) && cfg.controlRandomnessMode0_controlFeaturesMode1 == 0 % skip SS check when only one sample
        all_samples(q, :) = samples;
        disp('*************ALL SAMPLES AFTER 1ST SAMPLE ADDED*************');
        disp(all_samples);
        disp('LOWER & UPPER BOUNDS: ')
        disp(ss_loBound);
        disp(ss_upBound);
    else
        % keep creating new sample until appropriately similar
        
        % this while loop represents an alternative algorithm:
        %similarity_ok = false; % Initialize a flag to check similarity condition
        %while ~similarity_ok
        %    similarity_ok = true; % Assume the similarity condition is met
        %    for k = 1:size(all_samples, 1)
        %        similarity_score = calculate_similarity_two_list(all_samples(k, :), samples);
        %        if similarity_score < ss_loBound(end) || similarity_score > ss_upBound(end)
        %            similarity_ok = false; % Similarity condition is not met
        %            samples = create_one_sample(dimension_name, dimension_value, available_dimensions); % Generate a new sample
        %            break; % Exit the for loop to generate a new sample
        %        end
        %    end
        %end

        if cfg.controlRandomnessMode0_controlFeaturesMode1 == 0 
            while calculate_similarity_two_list(all_samples(1,:), samples) < ss_loBound || calculate_similarity_two_list(all_samples(1,:), samples) > ss_upBound
                samples = create_one_sample(dimension_name, dimension_value, available_dimensions); % generate a new sample
            end
        else
            while true
                samples = create_one_sample(dimension_name, dimension_value, available_dimensions); % generate a new sample
                if ~check_duplicate(samples, all_samples)
                    break;
                end
            end
        end

        all_samples(q, :) = samples;
        %disp('*************ALL SAMPLES AFTER ADDING A SAMPLE*************');
        %disp(all_samples);
    end


    % Define your list of numbers
    my_list = samples(1,:); % USED TO BE my_list = samples(i,:);
     
    % Find the next available file index
    fileIndex = q; % Use the loop index for file numbering
    objectNames{end+1} = ['Object Table_' sprintf('%03d', fileIndex) '.txt'];
    newFilename = [stim_iPath objectNames{end}];
    %newFilename = [stim_iPath 'Object Table_' sprintf('%03d', fileIndex) '.txt'];
    
    
    % Open a text file for writing
    fid = fopen(newFilename, 'w');
    
    % Write the text to the file
    fprintf(fid, 'Body:\t[%d]\n', my_list(1));
    fprintf(fid, 'BMain_Colour:\t[%d]\n', my_list(2));
    fprintf(fid, 'BComp_Colour:\t[%d]\n', my_list(3));
    fprintf(fid, 'BPattern:\t[%d]\n', my_list(4));
    fprintf(fid, 'Fractal:\t[%d]\n', my_list(5));
    fprintf(fid, 'Head:\t[%d]\n', my_list(6));
    fprintf(fid, 'HMain_Colour:\t[%d]\n', my_list(7));
    fprintf(fid, 'HComp_Colour:\t[%d]\n', my_list(8));
    fprintf(fid, 'HPattern:\t[%d]\n', my_list(9));
    fprintf(fid, 'Ear_Left_Type:\t[%d]\n', my_list(10));
    fprintf(fid, 'Ear_Right_Type:\t[%d]\n', my_list(11));
    fprintf(fid, 'Ear_Left_Length:\t[%d]\n', my_list(12));
    fprintf(fid, 'Ear_Right_Length:\t[%d]\n', my_list(13));
    fprintf(fid, 'Arm_Position:\t[%d]\n', my_list(14));
    fprintf(fid, 'Arm_Angle_Left:\t[%d]\n', my_list(15));
    fprintf(fid, 'Arm_Angle_Right:\t[%d]\n', my_list(16));
    fprintf(fid, 'Beak:\t[%d]\n', my_list(17));
    fclose(fid);
   
end

% --- generate objects
generate_object(cfg);

    % --- generate objects

    cfg_out.objectTables = objectNames;
    cfg_out.samples = all_samples;
    % --- collect generated filenames:
    objectFileNames   = {};
    objectFileFolders = {};
    dirinfo = dir([cfg.output_path '/Stimuli']);
    if isempty(dirinfo), sprintf('could not open %s\n',cfg.output_path), return, end
	
	% Filter out directories and hidden files
	isValidFile = ~[dirinfo.isdir] & ~startsWith({dirinfo.name}, '.');
	% Extract valid files
	validFiles = dirinfo(isValidFile);
	% Find files with '.gltf' extension
	gltfFiles = validFiles(endsWith({validFiles.name}, '.gltf'));
	% Sort the files by date from oldest to newest
	[~, sortIdx] = sort([gltfFiles.datenum]);
	sortedGltfFiles = gltfFiles(sortIdx);
	% Initialize cell arrays if empty
	if ~exist('objectFileFolders', 'var') || isempty(objectFileFolders)
    	objectFileFolders = {};
		objectFileNames = {};
	end
	% Populate the cell arrays with sorted files
	for j = 1:length(sortedGltfFiles)
    	cL = length(objectFileNames) + 1;
    	objectFileFolders{cL} = cfg.output_path;
    	objectFileNames{cL} = sortedGltfFiles(j).name; % (1:end-4) if needed
	end

%     for j=1:length(dirinfo)
%         if (dirinfo(j).isdir) || strcmp(dirinfo(j).name(1),'.' ),  continue, end
%         if ~isempty(findstr(dirinfo(j).name,'.gltf'))
%             cL = length(objectFileNames) + 1;
%             objectFileFolders{cL} = cfg.output_path;
%             objectFileNames{cL} = dirinfo(j).name;%(1:end-4);
%         end
%     end

cfg_out.objectFileNames   = objectFileNames;
cfg_out.objectFileFolders = objectFileFolders;

fprintf('\n generated %d objects \n', cfg.num_quaddles);

end



function [dimension_name, dimension_value, available_dimensions] = init_dimensions(controlRandomnessMode0_controlFeaturesMode1, nVaryingDimensions)
    % creating list 'samples', which contains dimensions of an object
    dimension_name = {
        'Body';
        'BMain_Colour';
        'BComp_Colour';
        'BPattern';
        'Fractal';
        'Head';
        'HMain_Colour';
        'HComp_Colour';
        'HPattern';
        'Ear_Left_Type';
        'Ear_Right_Type';
        'Ear_Left_Length';
        'Ear_Right_Length';
        'Arm_Position';
        'Arm_Angle_Left';
        'Arm_Angle_Right';
        'Beak'
        };
    % num options for each dimension
    dimension_value = dictionary( ...
        'Body', 7, ...
        'BMain_Colour', 11, ...
        'BComp_Colour', 11, ...
        'BPattern', 4, ...
        'Fractal', 94, ...
        'Head', 3, ...
        'HMain_Colour', 11, ...
        'HComp_Colour', 11, ...
        'HPattern', 4, ...
        'Ear_Left_Type', 3, ...
        'Ear_Right_Type', 3, ...
        'Ear_Left_Length', 2, ...
        'Ear_Right_Length', 2, ...
        'Arm_Position', 3, ...
        'Arm_Angle_Left', 2, ...
        'Arm_Angle_Right', 2, ...
        'Beak', 1);
    % which dimensions are available
    if controlRandomnessMode0_controlFeaturesMode1 == 0 % if nVaryingDimensions == 16, 17
        available_dimensions = {
            'Body';
            'BMain_Colour';
            'BComp_Colour';
            'BPattern';
            'Fractal';
            'Head';
            'HMain_Colour';
            'HComp_Colour';
            'HPattern';
            'Ear_Left_Type';
            'Ear_Right_Type';
            'Ear_Left_Length';
            'Ear_Right_Length';
            'Arm_Position';
            'Arm_Angle_Left';
            'Arm_Angle_Right';
            'Beak'
            };
    else % control features mode - choose how many dimensions are available to vary
        %disp(nVaryingDimensions);
        if nVaryingDimensions == 1
            available_dimensions = {'Body';};
        elseif nVaryingDimensions == 2
            available_dimensions = {'Body'; 'BMain_Colour';'BComp_Colour';};
        elseif nVaryingDimensions == 3
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';};
        elseif nVaryingDimensions == 4
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';};
        elseif nVaryingDimensions == 5
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';};
        elseif nVaryingDimensions == 6
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern';};
        elseif nVaryingDimensions == 7
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';};
        elseif nVaryingDimensions == 8
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';};
        elseif nVaryingDimensions == 9
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';};
        elseif nVaryingDimensions == 10
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';};
        elseif nVaryingDimensions == 11
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';'Ear_Left_Type';};
        elseif nVaryingDimensions == 12
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';'Ear_Left_Type';'Ear_Right_Type';};
        elseif nVaryingDimensions == 13
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';'Ear_Left_Type';'Ear_Right_Type';'Ear_Left_Length';};
        elseif nVaryingDimensions == 14
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';'Ear_Left_Type';'Ear_Right_Type';'Ear_Left_Length';'Ear_Right_Length';};
        elseif nVaryingDimensions == 15
            available_dimensions = {'Body';'BMain_Colour';'BComp_Colour';'BPattern';'Head';'HMain_Colour';'HComp_Colour';'HPattern'; 'Fractal';'Arm_Position';'Arm_Angle_Left';'Arm_Angle_Right';'Ear_Left_Type';'Ear_Right_Type';'Ear_Left_Length';'Ear_Right_Length';'Beak';};
        end
    end
end


function samples = create_one_sample(dimension_name, dimension_value, available_dimensions)

    samples = cell(numel(dimension_name),1);
    % Loop over each dimension
    %disp('AVAILABLE DIMENSION(S):');
    %disp(available_dimensions);
    for i = 1:numel(dimension_name)
        % Set the number of samples to take from each dimension
        num_samples = dimension_value(dimension_name(i));
        % Randomly sample numbers: if it is in an available dimension, then randomly sample one of it
        if ismember(dimension_name(i), available_dimensions)
            samples{i} = randi(num_samples + 1, 1) - 1; % randomly sample one of the available options
        else
            samples{i} = 0; % assign 0 if the dimension is not available
        end
    end
    samples = cell2mat(samples);
    samples = samples';
    for i = 1:length(samples(:,1))
        samples(i,:) = modify_list(samples(i,:));
    end
end




function generate_object(cfg)
% Make Quaddle in blender
if ~isfield(cfg,'export_png')
    cfg.export_png = 'False';
    cfg.export_fbx = 'False';
    cfg.export_gltf = 'True';
end
% cfg.blender_path = '/Applications/Blender.app/Contents/MacOS/Blender'; % Change this to your Blender path
% cfg.blender_file_path = '/Users/wenxuan/Desktop/blender-quaddle/makeQuaddle.blend'; % Change this to your makeQuaddle path
% cfg.python_script = '/Users/wenxuan/Desktop/blender-quaddle/parser.py'; % Change this to your Python script path
% cfg.blender_input_path = [pwd '/CONFIGS/StimConfig/'];
% cfg.output_path = [pwd '/CONFIGS/generated_quaddles/'];
%     
    command = sprintf('"%s" --background "%s" --python "%s" -- --input_path "%s" --output_path "%s" --export_fbx "%s" --export_png "%s" --export_gltf "%s"', ...
        cfg.blender_path, cfg.blender_file_path, cfg.python_script, cfg.blender_input_path, cfg.output_path, cfg.export_fbx, cfg.export_png, cfg.export_gltf);

    system(command);
end

% modify list function to help with similarity score + blender
function modified_list = modify_list(input_list)
    modified_list = input_list;
    % NOTE: This version is based on assigning a default gray color to patterns,
    % remove first IF statement if you want multiple color combinations.
    % Check Body Color and Pattern
    if modified_list(4) ~= 0 % if pattern is not solid
        modified_list(3) = 0; % assign white to comp color
    end
    if modified_list(2) > modified_list(3) % main color > comp color for body
        temp = modified_list(2);
        modified_list(2) = modified_list(3);
        modified_list(3) = temp;
    elseif modified_list(2) == modified_list(3) % main color = comp color for body
        modified_list(4) = 0; % change pattern to solid
    end
    % Check Head Color and Pattern
    if modified_list(9) ~= 0 % if pattern is not solid
        modified_list(8) = 0; % assign white to comp color
    end
    if modified_list(7) > modified_list(8) % main color > comp color for head
        temp = modified_list(7);
        modified_list(7) = modified_list(8);
        modified_list(8) = temp;
    elseif modified_list(7) == modified_list(8) % if main color = comp color for head
        modified_list(9) = 0; % change pattern to 0
    end
    % Check if BPattern is 0, if true, set BComp_Color to 0
    if modified_list(4) == 0
        modified_list(3) = 0;
    end
    % Check if HPattern is 0, if true, set HComp_Color to 0
    if modified_list(9) == 0
        modified_list(8) = 0;
    end
    % Modify Ear and Arm
    % Check if Ear_Left_Type is not 0, if true, set Ear_Left_Length to 0
    if modified_list(10) == 0
        modified_list(12) = 0;
    end
    % Check if Ear_Right_Type is not 0, if true, set Ear_Right_Length to 0
    if modified_list(11) == 0
        modified_list(13) = 0;
    end
    % Check arm position
    if modified_list(14) == 0 % no arm
        modified_list(15) = 0; % set left arm angle to 0
        modified_list(16) = 0; % set right arm angle to 0
    end
    if modified_list(14) == 1 % left arm only
        modified_list(16) = 0; % set right arm angle to 0
    end
    if modified_list(14) == 2 % right arm only
        modified_list(15) = 0; % set left arm angle to 0
    end
end


% calculating the similarity score (higher = more similar)
function score = calculate_similarity_two_list(list1, list2)
score = 0;
for i = 1:length(list1)
	if i == 1
		% Body shape, weight = 2
		weight = 2;
    elseif i == 2 || i == 3  || i == 4
		% Body color/pattern related dimensions, weight = 1.5
		weight = 1.5;
    elseif i == 5
	    % Fractal related dimensions, weight = 0.25
	    weight = 0.25;
    elseif i == 6
		% Head shape, weight = 1
		weight = 1;
    elseif i == 7 || i == 8  || i == 9
		% Head color/pattern related dimensions, weight = 0.75
		weight = 0.75;
    elseif i == 10 || i == 11 || i == 12 || i == 13
		% Ear related dimensions, weight = 0.25
		weight = 0.25;
	elseif i == 14 || i == 15 || i == 16
		% Arm related dimensions, weight = 0.75
		weight = 0.75;
	elseif i == 17
		% Beak, weight = 0.25
		weight = 0.25;
	else
		% Other dimensions, weight = 1
		weight = 1;
	end
	if list1(i) == list2(i)
		score = score + weight;
    end
end
disp(['Similarity Score: ', num2str(score)]);
end

function is_duplicate = check_duplicate(new_sample, all_samples)
        is_duplicate = any(ismember(all_samples, new_sample, 'rows'));
end
