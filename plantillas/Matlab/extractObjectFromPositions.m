function extractObjectFromPositions(imagePath, positionsFilePath, outputImagePath)
% Lee la imagen original
img = im2double(imread(imagePath));

% Lee las posiciones de los píxeles desde el archivo
pixelPositions = readmatrix(positionsFilePath, 'Delimiter', 'tab');

% Crear una máscara del objeto
[height, width, ~] = size(img);
objectMask = false(height, width);
for i = 1:size(pixelPositions, 1)
objectMask(pixelPositions(i, 1), pixelPositions(i+1, 1)) = true;
end

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

% Guardar la imagen del objeto
imwrite(objectImgCropped, outputImagePath);

fprintf('Imagen del objeto guardada en "%s".\n', outputImagePath);
end