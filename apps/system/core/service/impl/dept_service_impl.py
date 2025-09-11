# -*- coding: utf-8 -*-
"""
部门服务实现

@author: continew-admin
@since: 2025/9/11 10:00
"""

from typing import List

from ..dept_service import DeptService
from apps.system.core.model.resp.dept_dict_tree_resp import DeptDictTreeResp


class DeptServiceImpl(DeptService):
    """部门服务实现"""
    
    async def get_dict_tree(self) -> List[DeptDictTreeResp]:
        """
        获取部门字典树
        
        Returns:
            List[DeptDictTreeResp]: 部门字典树列表
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟的部门树结构数据，匹配参考项目格式
        
        # 模拟部门树数据
        dept_tree_data = [
            DeptDictTreeResp(
                key=1,
                parent_id=0,
                title="FlowMaster科技有限公司",
                sort=1,
                children=[
                    DeptDictTreeResp(
                        key="547887852587843590",
                        parent_id=1,
                        title="FlowMaster（北京）科技有限公司",
                        sort=1,
                        children=[
                            DeptDictTreeResp(
                                key="547887852587843591",
                                parent_id="547887852587843590",
                                title="研发部",
                                sort=1,
                                children=[
                                    DeptDictTreeResp(
                                        key="547887852587843595",
                                        parent_id="547887852587843591",
                                        title="研发一组",
                                        sort=1,
                                        children=None
                                    ),
                                    DeptDictTreeResp(
                                        key="547887852587843596",
                                        parent_id="547887852587843591",
                                        title="研发二组",
                                        sort=2,
                                        children=None
                                    )
                                ]
                            ),
                            DeptDictTreeResp(
                                key="547887852587843592",
                                parent_id="547887852587843590",
                                title="UI部",
                                sort=2,
                                children=None
                            ),
                            DeptDictTreeResp(
                                key="547887852587843593",
                                parent_id="547887852587843590",
                                title="测试部",
                                sort=3,
                                children=None
                            ),
                            DeptDictTreeResp(
                                key="547887852587843594",
                                parent_id="547887852587843590",
                                title="运维部",
                                sort=4,
                                children=None
                            )
                        ]
                    ),
                    DeptDictTreeResp(
                        key="547887852587843597",
                        parent_id=1,
                        title="FlowMaster（上海）科技有限公司",
                        sort=2,
                        children=[
                            DeptDictTreeResp(
                                key="547887852587843598",
                                parent_id="547887852587843597",
                                title="研发部",
                                sort=1,
                                children=[
                                    DeptDictTreeResp(
                                        key="547887852587843599",
                                        parent_id="547887852587843598",
                                        title="研发一组",
                                        sort=1,
                                        children=None
                                    )
                                ]
                            )
                        ]
                    ),
                    DeptDictTreeResp(
                        key="547887852587843600",
                        parent_id=1,
                        title="FlowMaster（深圳）科技有限公司",
                        sort=3,
                        children=[
                            DeptDictTreeResp(
                                key="547887852587843601",
                                parent_id="547887852587843600",
                                title="研发部",
                                sort=1,
                                children=[
                                    DeptDictTreeResp(
                                        key="547887852587843602",
                                        parent_id="547887852587843601",
                                        title="研发一组",
                                        sort=1,
                                        children=None
                                    )
                                ]
                            )
                        ]
                    ),
                    DeptDictTreeResp(
                        key="547887852587843603",
                        parent_id=1,
                        title="FlowMaster（广州）科技有限公司",
                        sort=4,
                        children=[
                            DeptDictTreeResp(
                                key="547887852587843604",
                                parent_id="547887852587843603",
                                title="研发部",
                                sort=1,
                                children=[
                                    DeptDictTreeResp(
                                        key="547887852587843605",
                                        parent_id="547887852587843604",
                                        title="研发一组",
                                        sort=1,
                                        children=None
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
        
        return dept_tree_data