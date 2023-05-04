# -*- coding: utf-8 -*-
import time

from JdSession import Session
from config import global_config
from exception import JDException
from log import logger
from timer import Timer
from utils import (
    save_image,
    open_image,
    convert_image,
    send_wechat
)


class Buyer(object):
    """
    京东买手
    """

    # 初始化
    def __init__(self):
        self.session = Session()
        # 微信推送
        self.enableWx = global_config.getboolean('messenger', 'enable')
        self.scKey = global_config.get('messenger', 'sckey')

    ############## 登录相关 #############
    # 二维码登录
    def loginByQrCode(self):
        if self.session.isLogin:
            logger.info('登录成功')
            return

        # download QR code
        qrCode = self.session.getQRcode()
        if not qrCode:
            raise JDException('二维码下载失败')

        fileName = 'QRcode.png'
        save_image(qrCode, fileName)
        new_file_name = 'QRcode.jpg'
        convert_image(fileName, new_file_name)
        open_image(new_file_name)
        logger.info('二维码获取成功，请打开京东APP扫描')
        # open_image(fileName)

        # get QR code ticket
        ticket = None
        retryTimes = 85
        for i in range(retryTimes):
            ticket = self.session.getQRcodeTicket()
            if ticket:
                break
            time.sleep(2)
        else:
            raise JDException('二维码过期，请重新获取扫描')

        # validate QR code ticket
        if not self.session.validateQRcodeTicket(ticket):
            raise JDException('二维码信息校验失败')

        logger.info('二维码登录成功')
        self.session.isLogin = True
        self.session.saveCookies()

    ############## 外部方法 #############
    def buyItemInStock(self, skuId, areaId, skuNum=1, stockInterval=3, submitRetry=3, submitInterval=5,
                       buyTime='2022-08-06 00:00:00'):
        """根据库存自动下单商品
        :skuId 商品sku
        :areaId 下单区域id
        :skuNum 购买数量
        :stockInterval 库存查询间隔（单位秒）
        :submitRetry 下单尝试次数
        :submitInterval 下单尝试间隔（单位秒）
        :buyTime 定时执行
        """
        self.session.fetchItemDetail(skuId)
        # self.session.addCartSku('100030339349', 1)
        # raise Exception('')
        # self.session.addCartSku('100030339349', 1)

        timer = Timer(buyTime)
        timer.start()
        count = 0
        while True:
            count += 1
            try:
                if not self.session.getItemStock(skuId, skuNum, areaId):
                    logger.info('不满足下单条件，{0}s后进行下一次查询'.format(stockInterval))
                else:
                    logger.info('{0} 满足下单条件，开始执行'.format(skuId))
                    if self.session.trySubmitOrder(skuId, skuNum, areaId, submitRetry, submitInterval):
                        logger.info('下单成功')
                        if self.enableWx:
                            send_wechat(
                                message='JdBuyerApp', desp='您的商品已下单成功，请及时支付订单', sckey=self.scKey)
                        return
            except Exception as e:
                logger.error(e)
            # time.sleep(stockInterval + random.randint(1, stockInterval))
            time.sleep(stockInterval)


if __name__ == '__main__':
    # 商品sku
    skuId = '100040452006'  # 申基医药 新型冠状抗原检测试剂盒(胶体金法) 快速检测 家用 25人份
    skuId = '100030339301'  # 振德（ZHENDE）N95过滤级医用防护口罩 四层防护非灭菌型独立白色款30包/盒 3D立体保暖口罩防尘独立包装

    skuId = '100030339325'  # 振德（ZHENDE）N95过滤级医用防护口罩 四层防护C形耳带灭菌独立白色30袋/盒 3D立体保暖口罩防尘
    skuId = '100030339349'  # 振德（ZHENDE）N95过滤级医用防护口罩 四层防护非灭菌型独立绿色款30包/盒 3D立体保暖口罩防尘独立包装
    skuId = '100030339301'  # 振德（ZHENDE）N95过滤级医用防护口罩 四层防护非灭菌型独立白色款30包/盒 3D立体保暖口罩防尘独立包装
    skuId = '3142374'  # 999三九感冒灵颗粒10g*9袋感冒药解热镇痛用于感冒引起的头痛发热鼻塞流涕咽痛

    skuId = '3026797'  # 美林布洛芬混悬液100ml1岁及以上婴幼儿退烧药儿童感冒药发烧强生小孩退热发热疼痛牙痛头痛肌肉痛颗粒
    skuId = '100028548841'  # 美林布洛芬混悬液35ml1岁及以上婴幼儿退烧药儿童感冒药发烧西安杨森强生小孩退热发热疼痛牙痛头痛颗粒

    skuId = '100040677948'  # 亿帆医药 布洛芬干混悬剂 34g:1.2g/瓶 60毫升/瓶 退烧 退热 牙痛 偏头痛 关节痛 肌肉痛 布洛芬混悬液

    skuId = '71571420639'  # 美林布洛芬混悬液35ml1岁及以上婴幼儿退烧药儿童感冒药发烧西安杨森强生小孩退热发热疼痛牙痛头痛颗粒
    skuId = '100026946401'  # 一洋 布洛芬混悬液2%* 100ml
    skuId = '100035432088'  # 吉浩 布洛芬混悬液 100毫升：2克*100ml
    skuId = '100034312889'  # 托恩 布洛芬混悬液60ml：1.2g用于儿童普通感冒或流行性感冒引起的发热

    skuId = '3120955'  # 太平 布洛芬
    skuId = '100050579951'  # 太平 布洛芬缓释胶囊0.3g*10粒*2板/盒 缓解轻至中度疼痛头痛神经痛牙痛痛经普通感冒流行性感冒引起的发热
    skuId = '3156948'  # 芬必得 布洛芬缓释胶囊 0.4g*24粒 退烧缓解牙痛头痛痛经肩痛肌痛劳损腱鞘炎滑囊炎关节肿痛发热
    skuId = '100007160491'  # 仁和 布洛芬缓释胶囊22粒/盒止痛药痛经退烧药成人牙痛肌肉关节痛神经痛头痛偏头痛感冒发热
    skuId = '100008738569'  # 仁和 布洛芬缓释胶囊22粒/盒止痛药痛经退烧药成人牙痛肌肉关节痛神经痛头痛偏头痛感冒发热

    # 区域id(可根据工程 area_id 目录查找)
    areaId = '19_1607_3155'
    # 购买数量
    skuNum = 1
    # 库存查询间隔(秒)
    stockInterval = 3
    # 监听库存后尝试下单次数
    submitRetry = 5
    # 下单尝试间隔(秒)
    submitInterval = 5
    # 程序开始执行时间(晚于当前时间立即执行，适用于定时抢购类)
    buyTime = '2022-12-27 10:59:59'

    buyer = Buyer()  # 初始化
    buyer.loginByQrCode()
    buyer.buyItemInStock(skuId, areaId, skuNum, stockInterval,
                         submitRetry, submitInterval, buyTime)
