"""Geometry module for defining and managing conductor geometry in electromagnetic field calculations.

This module provides classes and functions to define conductor geometries consisting of
straight line segments in 3D space. Each segment is either vertical or horizontal (parallel
to one of the coordinate axes) and is associated with a phase conductor for multi-phase
current systems.

Key concepts:
    - Geometry: A complete geometric model with segments, conductor phases, force masks, and field points.
    - Conductor: A series of connected waypoints defining a conductor path with associated radii and force masks.
    - WayPoints: A set of 3D coordinates defining a path in space.
    - Segment: A straight line connecting two consecutive waypoints, indexed by phase.

Typical usage:
    >>> conductors = [Conductor(X_A, Y_A, Z_A, phase=0, R=[0.02]*3)]
    >>> field_pts = WayPoints(X_field, Y_field, Z_field)
    >>> geom = fromConductorsWP(conductors, field_pts)
"""

import numpy as np
from dataclasses import dataclass
from typing import Final

SUBFIELD_SEPARATOR : Final = '.'
GEOM_VAR_NAME : Final = 'WPNT'
FELD_VAR_NAME : Final = 'MPRB'
FORC_VAR_NAME : Final = 'FMSK'
RADI_VAR_NAME: Final =  'RADI'
SAME_VAR_NAME : Final = 'PSAM'
PDST_VAR_NAME : Final = 'PDST'
PCNT_VAR_NAME: Final = 'PCNT'
CONN_VAR_NAME: Final = 'PCON'
DEFAULT_SEGMENT_RADIUS: Final = 0.02

COND_LETTERS : Final = 'ABCS'

GND_VAR_NAME : Final = 'GNDP'
SRC_VAR_NAME : Final = 'SRCP'


@dataclass
class Geometry:
    """Complete geometric definition of a multi-phase conductor system and field measurement points.
    
    Represents a conductor network consisting of straight segments defined by their start and end
    points, organized by phase. Includes field observation points and configuration information
    for force and field calculations.
    
    Attributes:
        XS (np.ndarray): X coordinates of segment start points (shape: [n_segments]).
        XE (np.ndarray): X coordinates of segment end points (shape: [n_segments]).
        YS (np.ndarray): Y coordinates of segment start points (shape: [n_segments]).
        YE (np.ndarray): Y coordinates of segment end points (shape: [n_segments]).
        ZS (np.ndarray): Z coordinates of segment start points (shape: [n_segments]).
        ZE (np.ndarray): Z coordinates of segment end points (shape: [n_segments]).
        NP (np.ndarray): Phase index for each segment (shape: [n_segments]). Integer array where
            each value indicates which phase (0-indexed) the segment belongs to.
        NF (np.ndarray): Force mask array (shape: [n_force_masks, n_segments]). Binary/integer mask
            used to select subsets of segments for force aggregation and output.
        NL (np.ndarray): Phase logical array (shape: [3, n_segments]). Boolean indicators for
            phases 0, 1, and 2 presence in each segment.
        X (np.ndarray): X coordinates of field observation points (shape: [n_points]).
        Y (np.ndarray): Y coordinates of field observation points (shape: [n_points]).
        Z (np.ndarray): Z coordinates of field observation points (shape: [n_points]).
        R (np.ndarray): Conductor radius for each segment (shape: [n_segments]). Used for
            corner approximation and field calculations.
    """
    XS: np.ndarray
    XE: np.ndarray
    YS: np.ndarray
    YE: np.ndarray
    ZS: np.ndarray
    ZE: np.ndarray
    NP: np.ndarray
    NF: np.ndarray
    NL: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    Z: np.ndarray
    # T: float
    # I: float
    R: np.ndarray
        
    def __init__(self, XS, XE, YS, YE, ZS, ZE, R, NP, NF, X, Y, Z, NL=np.array([])):
        """Initialize a Geometry object with segment and field point definitions.
        
        Validates that all input arrays have compatible shapes and initializes the geometry.
        All segment coordinate arrays must have the same shape, and all field point coordinate
        arrays must have matching shapes.
        
        Args:
            XS (np.ndarray): X coordinates of segment start points.
            XE (np.ndarray): X coordinates of segment end points.
            YS (np.ndarray): Y coordinates of segment start points.
            YE (np.ndarray): Y coordinates of segment end points.
            ZS (np.ndarray): Z coordinates of segment start points.
            ZE (np.ndarray): Z coordinates of segment end points.
            R (np.ndarray): Conductor radius for each segment.
            NP (np.ndarray): Phase index for each segment.
            NF (np.ndarray): Force mask array for segment selection.
            X (np.ndarray): X coordinates of field observation points.
            Y (np.ndarray): Y coordinates of field observation points.
            Z (np.ndarray): Z coordinates of field observation points.
            NL (np.ndarray, optional): Phase logical array. Defaults to empty array.
        
        Raises:
            SystemExit: If input array dimensions are inconsistent.
        """
        # Validate segment coordinates are compatible shapes
        if not (XS.shape == XE.shape and YS.shape == YE.shape and ZS.shape == ZE.shape and
                XS.shape == YS.shape and XS.shape == ZS.shape and XS.shape == NP.shape):
            raise ValueError('Geometry definition error: Segment coordinate dimensions must match')
        
        # Validate field points are compatible shapes
        if not (X.shape == Y.shape and X.shape == Z.shape):
            raise ValueError('Geometry definition error: Field point coordinate dimensions must match')     
        self.XS = XS #X coordinates of circuit segments start points
        self.XE = XE #X coordinates of circuit segments end points
        self.YS = YS #Y coordinates of circuit segments start points
        self.YE = YE #Y coordinates of circuit segments end points
        self.ZS = ZS #Z coordinates of circuit segments start points
        self.ZE = ZE #Z coordinates of circuit segments end points
        self.NP = NP #index of current branch for segments
        self.NF = NF #mask of segments for force output summation
        self.NL = NL
        self.X = X #X coordinates of field output points
        self.Y = Y #Y coordinates of field output points
        self.Z = Z #Z coordinates of field output points
        self.R = R #default radius of conductor using for corner approximation
        
    def getCircuitPhaseCount(self):
        """Calculate the number of phases in the circuit.
        
        Returns the count of distinct phases by examining the range of phase indices
        in the NP array.
        
        Returns:
            int: Number of phases (e.g., 3 for three-phase system).
        """
        return int(1 + self.NP.max() - self.NP.min())
        
    def rotateX(self):
        """Rotate the geometry 90 degrees around the X axis.
        
        Transforms coordinates: Y -> Z, Z -> -Y (right-hand rotation).
        Modifies the geometry in-place.
        """
        ys = -self.ZS
        ye = -self.ZE
        self.ZS = self.YS
        self.ZE = self.YE
        self.YS = ys
        self.YE = ye
                
    def rotateY(self):
        """Rotate the geometry 90 degrees around the Y axis.
        
        Transforms coordinates: X -> Z, Z -> -X (right-hand rotation).
        Modifies the geometry in-place.
        """
        xs = +self.ZS
        xe = +self.ZE
        self.ZS = -self.XS
        self.ZE = -self.XE
        self.XS = xs
        self.XE = xe        
        
    def rotateZ(self):
        """Rotate the geometry 90 degrees around the Z axis.
        
        Transforms coordinates: X -> Y, Y -> -X (right-hand rotation).
        Modifies the geometry in-place.
        """
        xs = -self.YS
        xe = -self.YE
        self.YS = self.XS
        self.YE = self.XE
        self.XS = xs
        self.XE = xe
            
    def mirrorZ(self):
        """Mirror the geometry across the XY plane (negate Z coordinates).
        
        Modifies the geometry in-place.
        """
        self.ZS = -self.ZS
        self.ZE = -self.ZE
    
    # Backwards compatibility alias
    mirriorZ = mirrorZ
                
    def mirrorX(self):
        """Mirror the geometry across the YZ plane (negate X coordinates).
        
        Modifies the geometry in-place.
        """
        self.XS = -self.XS
        self.XE = -self.XE
    
    # Backwards compatibility alias
    mirriorX = mirrorX        
        
    def mirrorY(self):
        """Mirror the geometry across the XZ plane (negate Y coordinates).
        
        Modifies the geometry in-place.
        """
        self.YS = -self.YS
        self.YE = -self.YE
    
    # Backwards compatibility alias
    mirriorY = mirrorY
    
@dataclass
class WayPoints:
    """A sequence of 3D waypoints defining a path in space.
    
    Represents a series of connected points that form a geometric path. Used as a basis
    for building conductor paths and field observation points.
    
    Attributes:
        X (list[float]): X coordinates of waypoints (length n).
        Y (list[float]): Y coordinates of waypoints (length n).
        Z (list[float]): Z coordinates of waypoints (length n).
    """
    X : list[float] # X coords array of way-points, size n
    Y : list[float] # Y coords array of way-points, size n
    Z : list[float] # Z coords array of way-points, size n
    def __init__(self, X = None, Y = None, Z = None):
        """Initialize a WayPoints object with 3D coordinates.
        
        Args:
            X (list[float], optional): X coordinates. Defaults to [].
            Y (list[float], optional): Y coordinates. Defaults to [].
            Z (list[float], optional): Z coordinates. Defaults to [].
        
        Raises:
            ValueError: If coordinate arrays have different lengths.
        """
        X = X if X is not None else []
        Y = Y if Y is not None else []
        Z = Z if Z is not None else []
        
        if not (len(X) == len(Y) == len(Z)):
            raise ValueError(f'Coordinate length mismatch: X({len(X)}), Y({len(Y)}), Z({len(Z)})')
        
        self.X = X
        self.Y = Y
        self.Z = Z     

@dataclass
class Conductor(WayPoints):
    """A conductor consisting of connected line segments with phase information.
    
    Extends WayPoints to include conductor-specific properties: phase index, conductor
    radii for each segment, and force masks for selecting segments in force calculations.
    The conductor is defined by n waypoints creating n-1 segments.
    
    Attributes:
        R (list[float]): Radius of each segment (length n-1). Defaults to DEFAULT_SEGMENT_RADIUS
            if not specified.
        F (list[list[int]]): Force masks for each output set (shape: [m, n-1]). Each row
            is a binary/integer mask selecting segments for force aggregation.
        N (int): Phase index (0-indexed) for this conductor (0, 1, or 2 for three-phase).
        segs (int): Number of segments (computed as len(X) - 1, read-only).
    """
    R : list[float] # radius of segments array, size n-1
    F : list[list[int]] # force masks, size (m, n-1)
    N : int # conductor phase index
    segs : int
    def __init__(self, X, Y, Z, N, F = None, R = None):
        """Initialize a Conductor with waypoints, phase index, and segment properties.
        
        Automatically computes the number of segments (n-1 from n waypoints) and validates
        or defaults segment radii and force masks.
        
        Args:
            X (list[float]): X coordinates of waypoints (length n, n >= 2).
            Y (list[float]): Y coordinates of waypoints (length n, n >= 2).
            Z (list[float]): Z coordinates of waypoints (length n, n >= 2).
            N (int): Phase index (0, 1, 2, etc.).
            F (list[list[int]] or int, optional): Force masks. Can be:
                - List of lists: each inner list is a mask of length (n-1)
                - Single int: converted to [[int]*segs]
                - None: no force masks. Defaults to None.
            R (list[float] or float, optional): Conductor radii. Can be:
                - List of floats: length must equal (n-1)
                - Single float: applied to all segments
                - None: defaults to DEFAULT_SEGMENT_RADIUS for each segment
                Defaults to None.
        
        Raises:
            ValueError: If mask or radius arrays have incorrect lengths.
        """    
        super().__init__(X, Y, Z)

        self.segs = len(X) - 1

        # Process force masks
        if F is None:
            F = []
        elif isinstance(F, list):
            if len(F) > 0 and any(len(f) != self.segs for f in F):
                raise ValueError(f'Force mask length != segment count {self.segs}')
        elif isinstance(F, int):
            F = [[F] * self.segs]
        else:
            F = []

        # Process radii
        if R is None:
            R = [DEFAULT_SEGMENT_RADIUS] * self.segs
        elif isinstance(R, list):
            if len(R) == 0:
                R = [DEFAULT_SEGMENT_RADIUS] * self.segs
            elif len(R) != self.segs:
                raise ValueError(f'Radius array length {len(R)} != segment count {self.segs}')
        elif isinstance(R, (int, float)):
            R = [float(R)] * self.segs
        else:
            R = [DEFAULT_SEGMENT_RADIUS] * self.segs

        self.R = R
        self.F = F
        self.N = N
        
def fromConductorsWP(conductors : list[Conductor], field_points: WayPoints):
    """Convert a list of Conductor objects to a unified Geometry object.
    
    Combines multiple conductor definitions (potentially different phases) into a single
    Geometry object suitable for electromagnetic field calculations. Extracts segment
    information from all conductors, constructs combined arrays, builds phase masks, and
    returns a Geometry instance.
    
    The function:
    1. Extracts segment start and end points from each conductor's waypoints
    2. Collects conductor radii and phase indices
    3. Expands force masks to full width (all segments) with zeros for other conductors
    4. Creates phase logical arrays (NL) indicating phase presence
    5. Returns a unified Geometry object
    
    Args:
        conductors (list[Conductor]): List of conductor definitions. Each conductor has
            waypoints that define segments and associated phase index, radii, and force masks.
        field_points (WayPoints): Field observation points where fields/forces will be calculated.
    
    Returns:
        Geometry: A complete geometry object with all segments, phases, field points, and
            force masks properly organized and indexed.
    
    Example:
        >>> cond_a = Conductor([0, 1, 2], [0, 1, 2], [0, 0, 0], N=0, R=0.02)
        >>> cond_b = Conductor([0, 1, 2], [0, -1, -2], [0, 0, 0], N=1, R=0.02)
        >>> field = WayPoints([0, 1], [0, 1], [1, 1])
        >>> geom = fromConductorsWP([cond_a, cond_b], field)
    """
    # Validate input
    if not conductors:
        raise ValueError('At least one conductor must be provided')
    
    # Extract segment endpoints using slicing (more efficient than slice objects)
    X1_list, X2_list = [], []
    Y1_list, Y2_list = [], []
    Z1_list, Z2_list = [], []
    R_list, N_list = [], []
    all_segs = 0
    # Sseg = slice(None, -1, +1)
    # Eseg = slice(+1, None, +1)

    for conductor in conductors:
        # Extract segment start and end points
        X1_list.extend(conductor.X[:-1])
        X2_list.extend(conductor.X[1:])
        Y1_list.extend(conductor.Y[:-1])
        Y2_list.extend(conductor.Y[1:])
        Z1_list.extend(conductor.Z[:-1])
        Z2_list.extend(conductor.Z[1:])
        R_list.extend(conductor.R)
        N_list.extend([conductor.N] * conductor.segs)
        all_segs += conductor.segs

    # Convert to numpy arrays for consistent interface
    X1 = np.array(X1_list)
    X2 = np.array(X2_list)
    Y1 = np.array(Y1_list)
    Y2 = np.array(Y2_list)
    Z1 = np.array(Z1_list)
    Z2 = np.array(Z2_list)
    R = np.array(R_list)
    N = np.array(N_list)
    
    # Convert field points to arrays
    X = np.array(field_points.X)
    Y = np.array(field_points.Y)
    Z = np.array(field_points.Z)
        
    # Build force masks with proper padding
    NF_list = []
    pre_segs = 0
    for conductor in conductors:
        segs = conductor.segs
        for f in conductor.F:
            # Create mask with zeros for other conductors
            padded_mask = [0] * pre_segs + list(f) + [0] * (all_segs - pre_segs - segs)
            NF_list.append(padded_mask)
        pre_segs += segs

    # Convert to numpy array (empty if no force masks)
    NF = np.array(NF_list) if NF_list else np.array([[]])
    
    # Create phase logical arrays - dynamically based on max phase
    max_phase = int(N.max())
    NL = np.stack([N == i for i in range(max_phase + 1)])
    
    return Geometry(X1, X2, Y1, Y2, Z1, Z2, R, N, NF, X, Y, Z, NL)
