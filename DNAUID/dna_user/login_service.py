import uuid
from typing import Optional

from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils import dna_api
from ..utils.utils import mask_uid_in_text
from ..utils.api.model import DNALoginRes, DNARoleListRes
from ..utils.database.models import DNABind, DNAUser
from ..utils.constants.constants import DNA_GAME_ID

complete_error_msg = "您尚未注册二重螺旋账号，请先在【皎皎角】进行角色绑定"
role_error_msg = "未找到二重螺旋角色，请在皎皎角注册账号后重新登录"


class DNALoginService:
    def __init__(self, bot: Bot, ev: Event):
        self.bot = bot
        self.ev = ev

    async def get_dev_code(self) -> str:
        return str(uuid.uuid4()).upper()

    async def dna_login(self, mobile: str, code: str, dev_code: Optional[str] = None):
        if not dev_code:
            dev_code = await self.get_dev_code()
        result = await dna_api.login(mobile, code, dev_code)
        if not result.is_success:
            return result.throw_msg()
        login_response = DNALoginRes.model_validate(result.data)

        if login_response.isComplete == 0:
            return complete_error_msg

        return await self.dna_login_token(login_response, dev_code)

    async def dna_login_token(self, login_response: DNALoginRes, dev_code: Optional[str] = None):
        return await self.dna_login_by_token(
            token=login_response.token,
            dev_code=dev_code,
            refresh_token=login_response.refreshToken,
            d_num=login_response.dNum,
        )

    async def dna_login_by_token(
        self,
        token: str,
        dev_code: Optional[str] = None,
        refresh_token: Optional[str] = "",
        d_num: Optional[str] = "",
    ):
        token = token.strip()
        if not token:
            return "token不能为空"
        if not dev_code:
            dev_code = await self.get_dev_code()
        role_list_response = await dna_api.get_role_list(token, dev_code)
        if not role_list_response.is_success:
            return role_list_response.throw_msg()
        if not role_list_response.data:
            return role_error_msg
        role_list = DNARoleListRes.model_validate(role_list_response.data)

        ev = self.ev
        user_id = ev.user_id
        bot_id = ev.bot_id
        group_id = ev.group_id

        role_ids_msg = []
        for role in role_list.roles:
            if role.gameId != DNA_GAME_ID:
                continue
            for show_vo in role.showVoList:
                uid = show_vo.roleId

                user: Optional[DNAUser] = await DNAUser.get_user_by_attr(user_id, bot_id, "uid", uid)

                if user:
                    update_data: dict[str, str] = {
                        "cookie": token,
                        "status": "",
                        "dev_code": dev_code,
                        "d_num": d_num or "",
                        "refresh_token": refresh_token or "",
                    }

                    await DNAUser.update_data_by_data(
                        select_data={"user_id": user_id, "bot_id": bot_id, "uid": uid},
                        update_data=update_data,
                    )
                else:
                    await DNAUser.insert_data(
                        user_id=user_id,
                        bot_id=bot_id,
                        cookie=token,
                        uid=uid,
                        status="",
                        dev_code=dev_code,
                        d_num=d_num or "",
                        refresh_token=refresh_token or "",
                    )

                res = await DNABind.insert_uid(user_id, bot_id, uid, group_id, lenth_limit=13)
                if res == 0 or (res == -2 and show_vo.isDefault == 1):
                    await DNABind.switch_uid_by_game(user_id, bot_id, uid)

                msg = {"name": show_vo.roleName, "uid": uid}
                if show_vo.isDefault == 1:
                    role_ids_msg.insert(0, msg)
                else:
                    role_ids_msg.append(msg)

        if not role_ids_msg:
            return complete_error_msg

        msg = ["登录成功, 已为您绑定以下角色:"]
        for role in role_ids_msg:
            msg.append(f"- 名字: {role['name']}")
        return "\n".join(msg)

    async def get_cookie(self) -> str:
        from ..utils.utils import is_uid_hidden

        # 检查 UID 是否应该被隐藏（优先群级设置，其次个人设置）
        uid_hidden = await is_uid_hidden(self.ev.user_id, self.ev.bot_id, self.ev.group_id)

        dna_users: list[DNAUser] = await DNAUser.select_dna_users(self.ev.user_id, self.ev.bot_id)
        if not dna_users:
            return "当前并未登录"

        msg: list[str] = []
        seen_tokens: set[str] = set()
        for raw_user in dna_users:
            if not raw_user.cookie or raw_user.cookie in seen_tokens:
                continue
            dna_user = await dna_api.check_cookie(raw_user)
            if not dna_user:
                continue
            if dna_user.cookie in seen_tokens:
                continue
            seen_tokens.add(dna_user.cookie)
            msg.append(f"二重螺旋UID: {dna_user.uid}")
            msg.append("token:")
            msg.append(dna_user.cookie)
            msg.append("--------------------------------")

        if not msg:
            return "未找到可用的二重螺旋token"

        result = "\n".join(msg)
        # 应用UID脱敏
        if uid_hidden:
            result = mask_uid_in_text(result)
        return result
