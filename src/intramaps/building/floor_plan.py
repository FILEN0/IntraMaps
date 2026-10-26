'''FloorPlan class definition.'''

class FloorPlan:
    '''The image of a floor and how to convert between its pixels and meters.

    The origin is always the top-left corner of the image, at pixel (0, 0).

    Attributes:
        floor_id: Identifier of the floor this image belongs to.
        image_path: Path of the image file.
        width_px: Width of the image in pixels.
        height_px: Height of the image in pixels.
        meters_per_pixel: Size of one pixel in meters.
    '''

    def __init__(self, floor_id: int, image_path: str, width_px: int, height_px: int,
                 meters_per_pixel: float):
        if not isinstance(floor_id, int):
            raise ValueError("floor_id must be an integer")
        if not isinstance(image_path, str) or not image_path.strip():
            raise ValueError("image_path must be a non-empty string")
        if isinstance(width_px, bool) or not isinstance(width_px, int) or width_px <= 0:
            raise ValueError("width_px must be a positive integer")
        if isinstance(height_px, bool) or not isinstance(height_px, int) or height_px <= 0:
            raise ValueError("height_px must be a positive integer")
        if (isinstance(meters_per_pixel, bool) or not isinstance(meters_per_pixel, (int, float))
                or meters_per_pixel <= 0):
            raise ValueError("meters_per_pixel must be a positive number")
        self.__floor_id = floor_id
        self.__image_path = image_path
        self.__width_px = width_px
        self.__height_px = height_px
        self.__meters_per_pixel = meters_per_pixel

    @property
    def floor_id(self) -> int:
        '''Returns the identifier of the floor.'''
        return self.__floor_id

    @property
    def image_path(self) -> str:
        '''Returns the path of the image file.'''
        return self.__image_path

    @property
    def width_px(self) -> int:
        '''Returns the width of the image in pixels.'''
        return self.__width_px

    @property
    def height_px(self) -> int:
        '''Returns the height of the image in pixels.'''
        return self.__height_px

    @property
    def meters_per_pixel(self) -> float:
        '''Returns the size of one pixel in meters.'''
        return self.__meters_per_pixel

    def to_meters(self, pixels: float) -> float:
        '''Converts a length or coordinate from pixels to meters.'''
        return pixels * self.__meters_per_pixel

    def to_pixels(self, meters: float) -> float:
        '''Converts a length or coordinate from meters to pixels.'''
        return meters / self.__meters_per_pixel
