import glob
import random
import unittest.mock as mock
import pytest
import discord
import requests
import tempfile
from discord import Interaction

from src.hellomegbot.commands import hellomeg


class TestHellomeg:
    """hellomeg.py のテストクラス"""

    def test_load_images_from_json_success(self, monkeypatch):
        """load_images_from_json関数の成功ケースのテスト"""
        # requestsのレスポンスをモック化
        mock_response = mock.MagicMock()
        mock_response.raise_for_status = mock.MagicMock()
        mock_response.json.return_value = [
            {"filepath": "images/user1/image1.png", "twitter_id": "user1"},
            {"filepath": "images/user2/image2.png", "twitter_id": "user2"}
        ]
        
        # requests.getをモック化
        mock_get = mock.MagicMock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)
        
        # 関数を実行
        result = hellomeg.load_images_from_json()
        
        # 結果を確認
        assert result is True
        assert len(hellomeg.hellomeg_images) == 2
        assert hellomeg.hellomeg_images[0]["filepath"] == "images/user1/image1.png"
        assert hellomeg.hellomeg_images[0]["twitter_id"] == "user1"
        assert hellomeg.hellomeg_images[1]["filepath"] == "images/user2/image2.png"
        assert hellomeg.hellomeg_images[1]["twitter_id"] == "user2"
        
        # 正しいURLでリクエストが行われたことを確認
        mock_get.assert_called_once_with(hellomeg.HELLOMEG_JSON_URL)

    def test_load_images_from_json_failure(self, monkeypatch):
        """load_images_from_json関数の失敗ケースのテスト"""
        # requestsのレスポンスをモック化して例外を発生させる
        def mock_get(url):
            raise requests.exceptions.RequestException("Mock error")
        monkeypatch.setattr(requests, "get", mock_get)
        
        # 関数を実行
        result = hellomeg.load_images_from_json()
        
        # 結果を確認
        assert result is False

    def test_setup_hellomeg_success(self, monkeypatch):
        """setup_hellomeg関数の成功ケースのテスト"""
        # load_images_from_jsonをモック化して成功を返す
        def mock_load_from_json():
            hellomeg.hellomeg_images = [
                {"filepath": "images/user1/image1.png", "twitter_id": "user1"},
                {"filepath": "images/user2/image2.png", "twitter_id": "user2"}
            ]
            return True
        monkeypatch.setattr(hellomeg, "load_images_from_json", mock_load_from_json)
        
        # 関数を実行
        hellomeg.setup_hellomeg()
        
        # 結果を確認
        assert len(hellomeg.hellomeg_images) == 2


    def test_set_config_all_params(self):
        """全てのパラメータを指定した場合のset_config関数のテスト"""
        # 初期値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability

        try:
            # 関数を実行
            hellomeg.set_config(fever_minute=30, ur_prob=0.05, sr_prob=0.25)

            # 設定値が正しく更新されているか確認
            assert hellomeg.hellomeg_fever_minute == 30
            assert hellomeg.hellomeg_ur_probability == 0.05
            assert hellomeg.hellomeg_sr_probability == 0.25
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability,
                sr_prob=original_sr_probability
            )

    def test_set_config_partial_params(self):
        """一部のパラメータのみ指定した場合のset_config関数のテスト"""
        # 初期値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability

        try:
            # fever_minuteのみ指定
            hellomeg.set_config(fever_minute=15)
            assert hellomeg.hellomeg_fever_minute == 15
            assert hellomeg.hellomeg_ur_probability == original_ur_probability
            assert hellomeg.hellomeg_sr_probability == original_sr_probability

            # ur_probのみ指定
            hellomeg.set_config(ur_prob=0.1)
            assert hellomeg.hellomeg_fever_minute == 15  # 前のテストで変更した値
            assert hellomeg.hellomeg_ur_probability == 0.1
            assert hellomeg.hellomeg_sr_probability == original_sr_probability

            # sr_probのみ指定
            hellomeg.set_config(sr_prob=0.3)
            assert hellomeg.hellomeg_fever_minute == 15  # 前のテストで変更した値
            assert hellomeg.hellomeg_ur_probability == 0.1  # 前のテストで変更した値
            assert hellomeg.hellomeg_sr_probability == 0.3
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability,
                sr_prob=original_sr_probability
            )

    @pytest.fixture
    def mock_interaction(self):
        """Discordのinteractionオブジェクトをモック化するフィクスチャ"""
        interaction = mock.MagicMock(spec=Interaction)
        interaction.response.send_message = mock.AsyncMock()
        interaction.guild_id = "12345"

        # created_atプロパティをモック化
        mock_created_at = mock.MagicMock()
        mock_created_at.minute = 0  # デフォルトは0分
        interaction.created_at = mock_created_at
        
        return interaction

    def test_register_command_normal_response(self, mock_interaction, monkeypatch):
        """通常のレスポンスをテスト"""
        # テスト前に元の値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            # FEVERモードに入らないよう、FEVERの分を明示的に設定（mock_interactionの分とは異なる値）
            hellomeg.set_config(fever_minute=30, ur_prob=0.03, sr_prob=0.18)
            
            # 画像情報をモック化（通常レスポンスでは使用しないが、コード内で参照されるため）
            mock_filepath = "assets/hellomeg/test_user/test_image.png"
            hellomeg.hellomeg_images = [{"filepath": mock_filepath, "twitter_id": "test_user"}]
            
            # random.randomの戻り値をモック化して通常レスポンスになるようにする
            # 確実に通常レスポンスになるよう、UR+SR確率より大きい値を設定
            test_random_value = hellomeg.hellomeg_ur_probability + hellomeg.hellomeg_sr_probability + 0.1
            
            # random.randomをモック化
            def mock_random():
                return test_random_value
            monkeypatch.setattr(random, "random", mock_random)
            
            # random.uniformをモック化（FEVER時に使用される）
            def mock_uniform(a, b):
                return test_random_value
            monkeypatch.setattr(random, "uniform", mock_uniform)
            
            # random.choiceをモック化
            def mock_choice(seq):
                return seq[0] if isinstance(seq[0], dict) else mock_filepath
            monkeypatch.setattr(random, "choice", mock_choice)
            
            # discord.Fileをモック化して実際のファイルを開かないようにする
            mock_file = mock.MagicMock()
            monkeypatch.setattr(discord, "File", lambda filepath: mock_file)
            
            # コマンドツリーをモック化
            mock_tree = mock.MagicMock()
            
            # register_commandを実行
            hellomeg.register_command(mock_tree)
            
            # 登録されたコマンド関数を取得
            command_func = mock_tree.command.return_value
            registered_func = command_func.call_args[0][0]
            
            # 登録された関数を実行
            import asyncio
            asyncio.run(registered_func(mock_interaction))
            
            # send_messageが正しく呼ばれたことを確認
            mock_interaction.response.send_message.assert_called_once_with(
                content=hellomeg.HELLOMEG_MESSAGE_MEDIUM
            )
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability,
                sr_prob=original_sr_probability
            )
            hellomeg.hellomeg_images = original_images

    def test_register_command_ur_response(self, mock_interaction, monkeypatch):
        """URレスポンスをテスト"""
        # テスト前に元の値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            # FEVERモードに入らないよう、FEVERの分を明示的に設定（mock_interactionの分とは異なる値）
            hellomeg.set_config(fever_minute=30, ur_prob=0.03)
            
            # 画像情報をモック化（URレスポンスでは使用しないが、コード内で参照されるため）
            mock_filepath = "assets/hellomeg/test_user/test_image.png"
            hellomeg.hellomeg_images = [{"filepath": mock_filepath, "twitter_id": "test_user"}]
            
            # random.randomの戻り値をモック化してURレスポンスになるようにする
            # 確実にURレスポンスになるよう、UR確率より小さい値を設定
            test_random_value = hellomeg.hellomeg_ur_probability / 2  # UR確率の半分の値
            
            # random.randomをモック化
            def mock_random():
                return test_random_value
            monkeypatch.setattr(random, "random", mock_random)
            
            # random.uniformをモック化（FEVER時に使用される）
            def mock_uniform(a, b):
                return test_random_value
            monkeypatch.setattr(random, "uniform", mock_uniform)
            
            # discord.Fileをモック化
            mock_file = mock.MagicMock()
            monkeypatch.setattr(discord, "File", lambda filepath: mock_file)
            
            # コマンドツリーをモック化
            mock_tree = mock.MagicMock()
            
            # register_commandを実行
            hellomeg.register_command(mock_tree)
            
            # 登録されたコマンド関数を取得
            command_func = mock_tree.command.return_value
            registered_func = command_func.call_args[0][0]
            
            # 登録された関数を実行
            import asyncio
            asyncio.run(registered_func(mock_interaction))
            
            # send_messageが正しく呼ばれたことを確認
            mock_interaction.response.send_message.assert_called_once_with(
                content=hellomeg.HEELOMEG_MESSAGE_LARGE
            )
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability
            )
            hellomeg.hellomeg_images = original_images

    def test_register_command_sr_response(self, mock_interaction, monkeypatch):
        """SRレスポンスをテスト"""
        # テスト前に元の値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            # FEVERモードに入らないよう、FEVERの分を明示的に設定（mock_interactionの分とは異なる値）
            hellomeg.set_config(fever_minute=30, ur_prob=0.03, sr_prob=0.18)
            
            # UR確率より大きく、UR+SR確率より小さい値を設定
            ur_prob = hellomeg.hellomeg_ur_probability
            sr_prob = hellomeg.hellomeg_sr_probability
            test_random_value = ur_prob + (sr_prob / 2)
            
            # random.randomをモック化
            def mock_random():
                return test_random_value
            monkeypatch.setattr(random, "random", mock_random)
            
            # 画像情報をモック化
            mock_filepath = "https://example.com/test_image.png"
            mock_image = {"filepath": mock_filepath, "twitter_id": "test_user"}
            hellomeg.hellomeg_images = [mock_image]
            
            # random.choiceをモック化
            def mock_choice(seq):
                return seq[0] if isinstance(seq[0], dict) else mock_filepath
            monkeypatch.setattr(random, "choice", mock_choice)
            
            # requests.getをモック化
            mock_response = mock.MagicMock()
            mock_response.raise_for_status = mock.MagicMock()
            mock_response.content = b"mock_image_content"
            def mock_get(url):
                # 正しいURLが構築されていることを確認
                assert url == f"https://hellomeg-assets.pages.dev/{mock_filepath}"
                return mock_response
            monkeypatch.setattr(requests, "get", mock_get)
            
            # tempfileをモック化
            mock_temp_file = mock.MagicMock()
            mock_temp_file.name = "/tmp/mock_image.png"
            monkeypatch.setattr(tempfile, "NamedTemporaryFile", lambda delete, suffix: mock_temp_file)
            
            # discord.Fileをモック化
            mock_file = mock.MagicMock()
            monkeypatch.setattr(discord, "File", lambda filepath: mock_file)
            
            # コマンドツリーをモック化
            mock_tree = mock.MagicMock()
            
            # register_commandを実行
            hellomeg.register_command(mock_tree)
            
            # 登録されたコマンド関数を取得
            command_func = mock_tree.command.return_value
            registered_func = command_func.call_args[0][0]
            
            # 登録された関数を実行
            import asyncio
            asyncio.run(registered_func(mock_interaction))
            
            # send_messageが正しく呼ばれたことを確認
            expected_content = f"{hellomeg.HELLOMEG_PNG_MESSAGE}[@test_user](<{hellomeg.TWITTER_PROFILE_URL}test_user>)"
            mock_interaction.response.send_message.assert_called_once_with(
                content=expected_content,
                file=mock_file
            )
            
            # 画像のダウンロードと一時ファイルの作成が行われたことを確認
            mock_temp_file.write.assert_called_once_with(b"mock_image_content")
            mock_temp_file.close.assert_called_once()
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability,
                sr_prob=original_sr_probability
            )
            hellomeg.hellomeg_images = original_images

    def test_register_command_fever_mode(self, mock_interaction, monkeypatch):
        """FEVERモードのテスト"""
        # テスト前に元の値を保存
        original_fever_minute = hellomeg.hellomeg_fever_minute
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # FEVERモードの分を設定
            fever_minute = 30
            hellomeg.set_config(fever_minute=fever_minute, ur_prob=0.03)
            
            # 画像情報をモック化（URレスポンスでは使用しないが、コード内で参照されるため）
            mock_filepath = "https://example.com/test_image.png"
            hellomeg.hellomeg_images = [{"filepath": mock_filepath, "twitter_id": "test_user"}]
            
            # interactionのcreated_atの分をFEVER分に設定
            mock_interaction.created_at.minute = fever_minute
            
            # random.randomをモック化（通常は通常レスポンスになる値）
            def mock_random():
                return 0.5
            monkeypatch.setattr(random, "random", mock_random)
            
            # random.uniformをモック化（FEVER時はUR+SR範囲内の値）
            ur_prob = hellomeg.hellomeg_ur_probability
            def mock_uniform(min_val, max_val):
                return ur_prob / 2  # UR確率の範囲内
            monkeypatch.setattr(random, "uniform", mock_uniform)
            
            # コマンドツリーをモック化
            mock_tree = mock.MagicMock()
            
            # register_commandを実行
            hellomeg.register_command(mock_tree)
            
            # 登録されたコマンド関数を取得
            command_func = mock_tree.command.return_value
            registered_func = command_func.call_args[0][0]
            
            # discord.Fileをモック化
            mock_file = mock.MagicMock()
            monkeypatch.setattr(discord, "File", lambda filepath: mock_file)
            
            # 登録された関数を実行
            import asyncio
            asyncio.run(registered_func(mock_interaction))
            
            # send_messageが正しく呼ばれたことを確認（FEVER時はUR）
            mock_interaction.response.send_message.assert_called_once_with(
                content=hellomeg.HEELOMEG_MESSAGE_LARGE
            )
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                fever_minute=original_fever_minute,
                ur_prob=original_ur_probability
            )
            hellomeg.hellomeg_images = original_images
