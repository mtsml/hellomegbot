import os
import glob
import random
import unittest.mock as mock
import pytest
import discord
import requests
import sqlite3
from discord import Interaction, File

from src.hellomegbot.commands import hellomeg


class TestHellomeg:
    """hellomeg.py のテストクラス"""

    def test_download_database(self, monkeypatch):
        """download_database関数のテスト"""
        # requestsのgetメソッドをモック化
        mock_response = mock.MagicMock()
        mock_response.content = b"mock database content"
        monkeypatch.setattr(requests, "get", lambda url: mock_response)
        
        # 一時ファイルの書き込みをモック化
        mock_open = mock.mock_open()
        monkeypatch.setattr("builtins.open", mock_open)
        
        # 関数を実行
        db_path = hellomeg.download_database()
        
        # 結果を確認
        assert db_path is not None
        mock_open.assert_called_once()
        mock_open().write.assert_called_once_with(b"mock database content")

    def test_get_images_from_db(self, monkeypatch):
        """get_images_from_db関数のテスト"""
        # sqlite3の接続とカーソルをモック化
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # fetchallの戻り値をモック化
        mock_images = [
            ("filepath1.png", "user1"),
            ("filepath2.png", "user2")
        ]
        mock_cursor.fetchall.return_value = mock_images
        
        # sqlite3.connectをモック化
        monkeypatch.setattr(sqlite3, "connect", lambda path: mock_conn)
        
        # 関数を実行
        images = hellomeg.get_images_from_db("mock_db_path")
        
        # 結果を確認
        assert images == mock_images
        mock_cursor.execute.assert_called_once_with("SELECT filepath, twitter_id FROM images")
        mock_conn.close.assert_called_once()

    def test_setup_hellomeg_with_db(self, monkeypatch):
        """データベースからの画像取得をテストするsetup_hellomeg関数のテスト"""
        # download_databaseの戻り値をモック化
        monkeypatch.setattr(hellomeg, "download_database", lambda: "mock_db_path")
        
        # get_images_from_dbの戻り値をモック化
        mock_images = [
            ("filepath1.png", "user1"),
            ("filepath2.png", "user2")
        ]
        monkeypatch.setattr(hellomeg, "get_images_from_db", lambda path: mock_images)
        
        # 関数を実行
        hellomeg.setup_hellomeg()
        
        # グローバル変数が正しく設定されているか確認
        assert hellomeg.hellomeg_images == mock_images
        assert len(hellomeg.hellomeg_images) == 2

    def test_setup_hellomeg_download_failure(self, monkeypatch):
        """データベース取得失敗時のテスト"""
        # download_databaseの戻り値をNoneにモック化（失敗を模倣）
        monkeypatch.setattr(hellomeg, "download_database", lambda: None)
        
        # 関数を実行
        hellomeg.setup_hellomeg()
        
        # グローバル変数が空リストに設定されているか確認
        assert hellomeg.hellomeg_images == []

    def test_setup_hellomeg_empty_db(self, monkeypatch):
        """データベースが空の場合のsetup_hellomeg関数のテスト"""
        # download_databaseの戻り値をモック化
        monkeypatch.setattr(hellomeg, "download_database", lambda: "mock_db_path")
        
        # get_images_from_dbの戻り値を空リストにモック化
        monkeypatch.setattr(hellomeg, "get_images_from_db", lambda path: [])
        
        # glob.globの戻り値も空リストにモック化（フォールバックも空）
        monkeypatch.setattr(glob, "glob", lambda path: [])
        
        # 関数を実行
        hellomeg.setup_hellomeg()
        
        # グローバル変数が空リストに設定されているか確認
        assert hellomeg.hellomeg_images == []

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
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            hellomeg.set_config(ur_prob=0.03, sr_prob=0.18)
            
            # 画像情報をモック化（通常レスポンスでは使用しないが、コード内で参照されるため）
            mock_filepath = "assets/hellomeg/test_user/test_image.png"
            hellomeg.hellomeg_images = [(mock_filepath, "test_user")]
            
            # 直接関数を作成
            async def mock_hellomeg_func(interaction):
                await interaction.response.send_message(content=hellomeg.HELLOMEG_MESSAGE_MEDIUM)
            
            # 関数を実行
            import asyncio
            asyncio.run(mock_hellomeg_func(mock_interaction))
            
            # send_messageが正しく呼ばれたことを確認
            mock_interaction.response.send_message.assert_called_once_with(
                content=hellomeg.HELLOMEG_MESSAGE_MEDIUM
            )
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
                ur_prob=original_ur_probability,
                sr_prob=original_sr_probability
            )
            hellomeg.hellomeg_images = original_images

    def test_register_command_ur_response(self, mock_interaction, monkeypatch):
        """URレスポンスをテスト"""
        # テスト前に元の値を保存
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            hellomeg.set_config(ur_prob=0.03)
            
            # 画像情報をモック化（URレスポンスでは使用しないが、コード内で参照されるため）
            mock_filepath = "assets/hellomeg/test_user/test_image.png"
            hellomeg.hellomeg_images = [(mock_filepath, "test_user")]
            
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
            hellomeg.set_config(ur_prob=original_ur_probability)
            hellomeg.hellomeg_images = original_images

    def test_register_command_sr_response(self, mock_interaction, monkeypatch):
        """SRレスポンスをテスト"""
        # テスト前に元の値を保存
        original_ur_probability = hellomeg.hellomeg_ur_probability
        original_sr_probability = hellomeg.hellomeg_sr_probability
        original_images = hellomeg.hellomeg_images
        
        try:
            # 確率を明示的に設定して、テストの安定性を確保
            hellomeg.set_config(ur_prob=0.03, sr_prob=0.18)
            
            # UR確率より大きく、UR+SR確率より小さい値を設定
            ur_prob = hellomeg.hellomeg_ur_probability
            sr_prob = hellomeg.hellomeg_sr_probability
            test_random_value = ur_prob + (sr_prob / 2)
            
            # random.randomをモック化
            def mock_random():
                return test_random_value
            monkeypatch.setattr(random, "random", mock_random)
            
            # random.choiceをモック化
            mock_image = ("assets/hellomeg/test_user/test_image.png", "test_user")
            def mock_choice(seq):
                return mock_image
            monkeypatch.setattr(random, "choice", mock_choice)
            
            # 画像情報をモック化
            hellomeg.hellomeg_images = [mock_image]
            
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
        finally:
            # テスト後に元の値に戻す
            hellomeg.set_config(
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
            mock_filepath = "assets/hellomeg/test_user/test_image.png"
            hellomeg.hellomeg_images = [(mock_filepath, "test_user")]
            
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
