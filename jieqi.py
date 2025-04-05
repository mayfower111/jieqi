from skyfield import api
from skyfield import almanac
from skyfield import almanac_east_asia as almanac_ea
from datetime import datetime
import pytz

def calculate_solar_terms(year, timezone='America/New_York'):
    # 初始化天文数据
    ts = api.load.timescale()
    
    # 优先使用本地de421.bsp文件
    try:
        eph = api.load('de421.bsp')
        print("成功加载星历表：de421.bsp")
    except Exception as e:
        print(f"加载本地de421.bsp失败：{str(e)}")
        print("尝试加载在线星历表...")
        try:
            eph = api.load('https://raw.githubusercontent.com/skyfielders/python-skyfield/master/ci/de421.bsp')
            print("成功加载在线星历表")
        except Exception as e:
            raise Exception("无法加载星历表，请确保de421.bsp文件存在或网络连接正常。")
    
    # 转换输入的日期字符串为datetime对象并设置时区
    try:
        local_tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"错误：未知时区 '{timezone}'，将使用默认时区 'America/New_York'")
        local_tz = pytz.timezone('America/New_York')

    try:
        # 设置年份的起始和结束日期
        start_formatted = f"{year}-01-01"
        end_formatted = f"{year}-12-31"
        
        start = datetime.strptime(start_formatted, '%Y-%m-%d')
        end = datetime.strptime(end_formatted, '%Y-%m-%d')
        # 为datetime对象添加时区信息
        start = local_tz.localize(start)
        end = local_tz.localize(end)

        # 计算节气
        t0 = ts.from_datetime(start)
        t1 = ts.from_datetime(end)
        
        t, tm = almanac.find_discrete(t0, t1, almanac_ea.solar_terms(eph))
        
        # 打印结果
        print(f"\n{start_formatted} 至 {end_formatted} 期间的24节气（{timezone}时区）：")
        print("-" * 50)
        print("节气\t\t日期时间")
        print("-" * 50)
        
        for tmi, ti in zip(tm, t):
            # 转换时间到指定时区
            utc_time = ti.utc_datetime()
            local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            # 格式化输出
            print(f"{almanac_ea.SOLAR_TERMS_ZHS[tmi]:<10}\t{local_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        print(f"计算节气时发生错误：{str(e)}")

def get_timezone_choice():
    print("\n请选择时区：")
    print("1. 美国东部时间 (America/New_York) [默认]")
    print("2. 中国时间 (Asia/Shanghai)")
    print("3. 英国时间 (Europe/London)")
    
    choice = input("请输入选项编号 [1-3]，直接回车选择默认时区: ")
    
    timezone_map = {
        '1': 'America/New_York',
        '2': 'Asia/Shanghai',
        '3': 'Europe/London'
    }
    
    return timezone_map.get(choice, 'America/New_York')

def main():
    print("欢迎使用24节气查询工具！")
    print("请输入年份（例如：2024）查询全年节气")
    
    while True:
        try:
            year_input = input("\n请输入年份，输入q退出：")
            
            if year_input.lower() == 'q':
                print("感谢使用，再见！")
                break
            
            try:
                year = int(year_input)
                if year < 1900 or year > 2100:
                    print("错误：请输入1900-2100之间的年份")
                    continue
            except ValueError:
                print("错误：请输入有效的年份数字")
                continue
                
            timezone = get_timezone_choice()
            calculate_solar_terms(year, timezone)
            
        except Exception as e:
            print(f"发生错误：{str(e)}")

if __name__ == '__main__':
    main()