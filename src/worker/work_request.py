from typing import *
import multiprocessing as mp
import traceback

from hapi import *

from worker.work_result import WorkResult

from utils.log import *
from utils.metadata.config import Config
from utils.graphing.band import Band, Bands
from utils.hapiest_util import echo
from utils.metadata.hapi_metadata import HapiMetaData
from utils.fetch_error import FetchErrorKind, FetchError


class WorkFunctions:
    @staticmethod
    def start_hapi(**kwargs) -> bool:
        """
        Initilizes the hapi database (i.e. loads all data into RAM).
        """
        print('Initializing hapi db...')
        try:
            db_begin(Config.data_folder)
            del LOCAL_TABLE_CACHE['sampletab']
            print('Done initializing hapi db...')
        except Exception as e:
            print('Error initializing hapi db...' + str(e))
            return False
        return True

    graph_type_map = {
        "Voigt": absorptionCoefficient_Voigt,
        "Lorentz": absorptionCoefficient_Lorentz,
        "Gauss": absorptionCoefficient_Gauss,
        "SD Voigt": absorptionCoefficient_SDVoigt,
        "Galatry": absorptionCoefficient_Doppler,
        "HT": absorptionCoefficient_HT
    }

    instrumental_fn_map = {
        "rectangular": SLIT_RECTANGULAR,
        "triangular": SLIT_TRIANGULAR,
        "gaussian": SLIT_GAUSSIAN,
        "diffraction": SLIT_DIFFRACTION,
        "michelson": SLIT_MICHELSON,
        "dispersion": SLIT_DISPERSION
    }

    @staticmethod
    def graph_bands(TableName: str, **kwargs) -> Bands:
        """
        The following set of local functions were supplied by R.V. Kochanov, modified / refactored by Joshua Karns
        @returns the bands for the table!
        """

        def make_band_index():
            """
            Create the band index.
            Band index is a dictionary of the format:
                DICT[BAND] = IDS,
                where BAND = (global_upper_quanta,global_lower_quanta)   (i.e. a tuple consisting from two parameters)
                IDS = indexes of the lines in LOCAL_TABLE_HASH corresponding to the BAND
            """
            data = LOCAL_TABLE_CACHE[TableName]['data']
            band2index = {}

            def process_band(params):
                """
                params should be a 3-tuple that contains (global_upper_quanta, global_lower_quanta, index)
                """
                band2index.setdefault((params[0], params[1]), []).append(params[2])

            quanta_with_index = zip(data['global_upper_quanta'], data['global_lower_quanta'], range(0, len(data['global_lower_quanta'])))
            list(map(process_band, quanta_with_index))

            return band2index

        def get_parameters(ids, params = ('nu', 'sw')):
            """
            Get line parameters as a columns from the LOCAL_TABLE_HASH
            using the ID numbers. Parameter names are specified in PARS.
            """
            data = LOCAL_TABLE_CACHE[TableName]['data']
            return zip(*list(map(lambda id: list(map(lambda par: data[par][id], params)), ids)))

        band2index = make_band_index()

        def get_band(band) -> Band:
            ids = band2index[band]
            nu, sw = get_parameters(ids)
            return Band(nu, sw, "{} -> {}".format(band[0].strip(), band[1].strip()))

        return Bands(list(map(get_band, band2index.keys())), TableName)


    @staticmethod
    def convolve_spectrum(x, y, instrumental_fn: str, Resolution: float, AF_wing: float):
        """
        Applies an instrumental function to (x, y) coordinates if one was selected.
        
        @returns the original (x, y) coordinates if no instrumental function was selected,
                otherwise it applies it and returns the result.
        """
        instrumental_fn = instrumental_fn.lower()
        if instrumental_fn not in WorkFunctions.instrumental_fn_map:
            return x, y
        else:
            newx, newy, i, j, slit = convolveSpectrum(x, y, Resolution=Resolution, AF_wing=AF_wing,
                                                      SlitFunction=WorkFunctions.instrumental_fn_map[instrumental_fn])
            return newx, newy

    @staticmethod
    def graph_absorption_coefficient(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            **kwargs) -> Union[Bands, Exception]:
        """
        Generates coordinates for absorption coeffecient graph.
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        # absorptionCoefficient_Doppler functions do not use Diluent
        if WorkFunctions.graph_type_map[graph_fn] == WorkFunctions.graph_type_map["Galatry"]:
            x, y = WorkFunctions.graph_type_map[graph_fn](
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                HITRAN_units=False,
                WavenumberRange=WavenumberRange,
                WavenumberStep=WavenumberStep,
                WavenumberWing=WavenumberWing,
                WavenumberWingHW=WavenumberWingHW) 
        else:
            x, y = WorkFunctions.graph_type_map[graph_fn](
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                Diluent=Diluent,
                HITRAN_units=False,
                WavenumberRange=WavenumberRange,
                WavenumberStep=WavenumberStep,
                WavenumberWing=WavenumberWing,
                WavenumberWingHW=WavenumberWingHW)
        result = Bands([Band(x, y, "Absorption Coef." + title)], "Absorption Coef. " + title)
        result.use_scatter_plot = False
        return result

    @staticmethod
    def graph_absorption_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        Generates coordinates for absorption spectrum graph.
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment = { 'l': path_length }
        x, y = absorptionSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }

    @staticmethod
    def graph_radiance_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, temp=296.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        Generates coordinates for radiance spectrum graph.
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment['l'] = path_length
        x, y = radianceSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }

    @staticmethod
    def graph_transmittance_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        Generates coordinates for transmittance spectrum graph.
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment = {'l': path_length}
        x, y = transmittanceSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }


    @staticmethod
    def fetch(data_name: str, iso_id_list: List[int], numin: float, numax: float,
                  parameter_groups: List[str] = (), parameters: List[str] = (), **kwargs) -> Union[
        Dict[str, List[str]], 'FetchError']:
        """
        Method handles verification of user input for fetch function.
        """
        if len(iso_id_list) == 0:
            return FetchError(FetchErrorKind.BadIsoList,
                              'Fetch Failure: Iso list cannot be empty.')
        try:
            fetch_by_ids(data_name, iso_id_list, numin, numax, parameter_groups, parameters)
            hmd = HapiMetaData(data_name, iso_id_list, numin, numax)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            debug('Fetch error: ', e)
            as_str = str(e)
            # Determine whether the issue is an internet issue or something else
            if 'connect' in as_str:
                return FetchError(
                    FetchErrorKind.BadConnection,
                    'Bad connection: Failed to connect to send request. Check your connection.')
            else:
                return FetchError(
                    FetchErrorKind.FailedToRetreiveData,
                    'Fetch failure: Failed to fetch data (connected successfully, received HTTP error as response)')
        return { 'all_tables': list(tableList()) }
   

    @staticmethod
    def get_table(table_name: str) -> Optional[Dict[str, Any]]:
        if table_name in LOCAL_TABLE_CACHE:
            return LOCAL_TABLE_CACHE[table_name]
        else:
            return None

    
    @staticmethod
    def save_table(table: Dict[str, Any], name: str, **kwargs):
        """
        Saves the modified table in the local table cache and on disk.
        """
        try:
            if name in LOCAL_TABLE_CACHE:
                del LOCAL_TABLE_CACHE[name]
            LOCAL_TABLE_CACHE[name] = table
            cache2storage(TableName=name)
            return True
        except:
            return False

    @staticmethod
    def table_meta_data(table_name: str):
        """
        Initilizes meta data file.
        """
        if table_name == None or table_name == '':
            return None
        table = LOCAL_TABLE_CACHE[table_name]['data']
        header = LOCAL_TABLE_CACHE[table_name]['header']
        parameters = list(table.keys())
        wn_min = min(LOCAL_TABLE_CACHE[table_name]['data']['nu'])
        wn_max = max(LOCAL_TABLE_CACHE[table_name]['data']['nu'])
        length = header['number_of_rows']
        return echo(length=length, header=header, parameters=parameters, wn_min=wn_min, wn_max=wn_max)

    @staticmethod
    def table_names(**kwargs):
        """
        Returns all table names in local cache.
        """
        table_names = []
        for (table_name, table) in LOCAL_TABLE_CACHE.items():
            table_names.append(table_name)

        return echo(table_names=table_names)

    @staticmethod
    def select(TableName: str, DestinationTableName: str = QUERY_BUFFER, ParameterNames: List[str] = None,
                   Conditions: List[Any] = None, Output: bool = False, File=None, **kwargs):
        """
        Attempts to call the select() method from hapi.
        """
        select(TableName=TableName, DestinationTableName=DestinationTableName, ParameterNames=ParameterNames,
              Conditions=Conditions, Output=Output, File=File)
        hmd = HapiMetaData(DestinationTableName)
        WorkFunctions.save_table(LOCAL_TABLE_CACHE[TableName], table_name=DestinationTableName)

        return echo(new_table_name=DestinationTableName, all_tables=list(tableList()))

class WorkRequest:
    def __init__(self, job_id: int, work_type: Any, work_args: Dict[str, Any]):
        self.job_id = job_id
        self.work_type = work_type
        self.work_args = work_args

    WorkType = int

    START_HAPI: WorkType = 0
    END_WORK_PROCESS: WorkType = 1
    FETCH: WorkType = 2
    ABSORPTION_COEFFICIENT: WorkType = 3
    TABLE_META_DATA: WorkType = 4
    GET_TABLE: WorkType = 5
    SAVE_TABLE: WorkType = 6
    TABLE_NAMES: WorkType = 7
    SELECT: WorkType = 8
    TRANSMITTANCE_SPECTRUM: WorkType = 9
    RADIANCE_SPECTRUM: WorkType = 10
    ABSORPTION_SPECTRUM: WorkType = 11
    BANDS: WorkType = 12

    WORKQ: mp.Queue = mp.Queue()
    RESULTQ: mp.Queue = mp.Queue()

    WORKER: 'Work' = None

    WORK_FUNCTIONS: Dict[WorkType, Callable] = {}

    def do_work(self) -> Any:
        """
        Executes the appropriate function, based on the specified work_type in the work request.
        """
        if self.work_type in WorkRequest.WORK_FUNCTIONS:
            fn = WorkRequest.WORK_FUNCTIONS[self.work_type]
            exec_res = fn(**self.work_args)
            return WorkResult(self.job_id, exec_res)

        return WorkResult(self.job_id, False)

    @staticmethod
    def start_work_process():
        WorkRequest.WORKER = Work()


class Work:
    @staticmethod
    def WORK_FUNCTION(workq: mp.Queue, resultq: mp.Queue) -> int:
        """
        Handles the calling of most hapi functions.
        """
        WorkRequest.WORK_FUNCTIONS = {
            WorkRequest.START_HAPI: WorkFunctions.start_hapi,
            WorkRequest.FETCH: WorkFunctions.fetch,
            WorkRequest.ABSORPTION_COEFFICIENT: WorkFunctions.graph_absorption_coefficient,
            WorkRequest.GET_TABLE: WorkFunctions.get_table,
            WorkRequest.SAVE_TABLE: WorkFunctions.save_table,
            WorkRequest.TABLE_NAMES: WorkFunctions.table_names,
            WorkRequest.TABLE_META_DATA: WorkFunctions.table_meta_data,
            WorkRequest.SELECT: WorkFunctions.select,
            WorkRequest.ABSORPTION_SPECTRUM: WorkFunctions.graph_absorption_spectrum,
            WorkRequest.TRANSMITTANCE_SPECTRUM: WorkFunctions.graph_transmittance_spectrum,
            WorkRequest.RADIANCE_SPECTRUM: WorkFunctions.graph_radiance_spectrum,
            WorkRequest.BANDS: WorkFunctions.graph_bands

        }

        WorkFunctions.start_hapi(**{})
        def print_tb(tb, exc_value):
            print('\n'.join([''] + traceback.format_tb(tb) + [str(exc_value)]).replace('\n', '\n    |   ') + '\n')


        while True:
            work_request = workq.get()
            if work_request.work_type == WorkRequest.END_WORK_PROCESS:
                return 0
            else:
                result = None
                try:
                    result = work_request.do_work()
                except Exception as e:
                    exc_ty, exc_val, exc_tb = sys.exc_info()
                    print_tb(exc_tb, exc_val)
                    debug('Error executing work request: ', e, type(e), result)
                    result = WorkResult(e, False)
                finally:
                    resultq.put(result)

    def __init__(self):
        self.process: mp.Process = mp.Process(target=Work.WORK_FUNCTION, args=(WorkRequest.WORKQ, WorkRequest.RESULTQ))
        self.process.start()
