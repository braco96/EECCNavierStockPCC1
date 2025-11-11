function separateObjectsWithMaxGapAndMinSize(imagePath, outputDir, maxGap, minSize, saveAll, name)
% Verifica y crea el directorio de salida
if ~exist(outputDir, 'dir')
mkdir(outputDir);
end

% Lee la imagen y la convierte a double [0,1]
img = im2double(imread(imagePath));

% Si es escala de grises, convertir a RGB
if size(img,3) == 1
img = repmat(img,[1 1 3]);
end

[height, width, ~] = size(img);

% Crear una máscara donde el foreground (no blanco) sea verdadero
nonWhiteMask = any(img < 1, 3); 

% Operación morfológica de cierre para unir componentes separadas por menos de maxGap píxeles
se = strel('square', maxGap+1); 
bwClosed = imclose(nonWhiteMask, se);

% Encuentra las componentes conectadas (objetos)
cc = bwconncomp(bwClosed);

objeto_count = 0;
largestObjectSize = 0;
largestObjectImg = [];
largestObjectName = '';

for i = 1:cc.NumObjects
pixelList = cc.PixelIdxList{i};
objectSize = numel(pixelList);  % Tamaño del objeto en píxeles

% Verificar si el objeto supera el tamaño mínimo
if objectSize >= minSize
objeto_count = objeto_count + 1;

% Crear la máscara del objeto actual
objectMask = false(height, width);
objectMask(pixelList) = true;

% Extraer el objeto de la imagen original
objectImg = img;
% Opcional: Si quieres mostrar sólo el objeto en un fondo blanco:
% objectImg(~repmat(objectMask, [1, 1, 3])) = 1;

% Recortar el objeto a su bounding box
stats = regionprops(objectMask, 'BoundingBox');
bbox = stats.BoundingBox;
x = round(bbox(1)); y = round(bbox(2));
w = round(bbox(3)); h = round(bbox(4));

objectImgCropped = objectImg(y:y+h-1, x:x+w-1, :);

% Guardar el objeto si saveAll es true
if saveAll
outputName = fullfile(outputDir, sprintf('isobarras_%d.png', objeto_count));
imwrite(objectImgCropped, outputName);
end

% Si saveAll es false, guardar solo el más grande
if ~saveAll && objectSize > largestObjectSize
largestObjectSize = objectSize;
largestObjectImg = objectImgCropped;
largestObjectName = fullfile(outputDir, name);
end
end
end

% Guardar el objeto más grande si saveAll es false
if ~saveAll && ~isempty(largestObjectImg)
imwrite(largestObjectImg, largestObjectName);
end

% Guardar la columna central del objeto pequeño
if saveAll
for i = 1:cc.NumObjects
pixelList = cc.PixelIdxList{i};
objectSize = numel(pixelList);  % Tamaño del objeto en píxeles

% Verificar si el objeto supera el tamaño mínimo
if objectSize >= minSize
% Crear la máscara del objeto actual
objectMask = false(height, width);
objectMask(pixelList) = true;

% Extraer el objeto de la imagen original
objectImg = img;
% Opcional: Si quieres mostrar sólo el objeto en un fondo blanco:
% objectImg(~repmat(objectMask, [1, 1, 3])) = 1;

% Recortar el objeto a su bounding box
stats = regionprops(objectMask, 'BoundingBox');
bbox = stats.BoundingBox;
x = round(bbox(1)); y = round(bbox(2));
w = round(bbox(3)); h = round(bbox(4));

objectImgCropped = objectImg(y:y+h-1, x:x+w-1, :);

% Guardar la columna central del objeto pequeño
midCol = round(w / 2);
columnImg = objectImgCropped(:, midCol, :);
columnImg = reshape(columnImg, [h, 1, 3]); % Convertir a una tira de píxeles
columnOutputName = fullfile(outputDir, 'columna_colores.png');
imwrite(columnImg, columnOutputName);
end
end
end

fprintf('Objetos separados y guardados en "%s" con tamaño mínimo de %d píxeles.\n', outputDir, minSize);
end
