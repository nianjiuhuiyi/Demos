import paddlehub as hub
from pprint import pprint

lda_news = hub.Module(name="lda_news")
jsd, hd = lda_news.cal_doc_distance(doc_text1="今天的天气如何，适合出去游玩吗", doc_text2="感觉今天的天气不错，可以出去玩一玩了")
# jsd = 0.003109, hd = 0.0573171
print(jsd)

lda_sim = lda_news.cal_query_doc_similarity(query='百度搜索引擎', document='百度是全球最大的中文搜索引擎、致力于让网民更便捷地获取信息，找到所求。百度超过千亿的中文网页数据库，可以瞬间找到相关的搜索结果。')
# LDA similarity = 0.06826

text = """
    本发明公开了一种永磁电机驱动的纯电动大巴车坡道起步防溜策略，即本策略当制动踏板已踩下、永磁电机转速小于设定值并持续一定时间，
    整车控制单元产生一个刹车触发信号，当油门踏板开度小于设定值，且档位装置为非空档时，电机控制单元产生一个防溜功能使能信号并自动进入
    防溜控制使永磁电机进入转速闭环控制于某个目标转速，若整车控制单元检测到制动踏板仍然踩下，则限制永磁电机输出力矩，否则，
    恢复永磁电机输出力矩；当整车控制单元检测到油门踏板开度大于设置值、档位装置为空档或手刹装置处于驻车位置，则退出防溜控制，
    同时切换到力矩控制。本策略无需更改现有车辆结构或添加辅助传感器等硬件设备，实现车辆防溜目的。
"""
# results = lda_news.cal_doc_keywords_similarity('百度是全球最大的中文搜索引擎、致力于让网民更便捷地获取信息，找到所求。百度超过千亿的中文网页数据库，可以瞬间找到相关的搜索结果。')
results = lda_news.cal_doc_keywords_similarity(text)
pprint(results)