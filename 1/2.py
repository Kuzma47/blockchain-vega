from copy import deepcopy
from typing import List, Tuple, Optional
import json
import hashlib

class Transaction:
    def __init__(self, tx_id: int, amount: float, message: str):
        self.id: int = tx_id
        self._amount: float = amount
        self._message: str = message

    def json(self) -> str:
        data: dict = {
            'tx_id': self.id,
            'amount': self._amount,
            'message': self._message
        }
        return json.dumps(data)

    def __eq__(self, other) -> bool:
        return hash(self.json()) == hash(other.json())

    def __repr__(self) -> str:
        return self.json()


class MerkleNode:
    def __init__(self, left: Optional['MerkleNode'], right: Optional['MerkleNode'], hash_value: str, tid: str):
        self.left: Optional[MerkleNode] = left
        self.right: Optional[MerkleNode] = right
        self.hash_value: str = hash_value
        self.tid: str = tid


class MerkleTree:
    def __init__(self, transactions: List[Transaction]):
        self._transactions: List[Transaction] = transactions
        self._leaves: List[MerkleNode] = [MerkleNode(None, None, MerkleTree.sha256(tx.json()), str(tx.id)) for tx in self._transactions]
        print([(node.tid, node.hash_value) for node in self._leaves])
        self._root: Optional[MerkleNode] = self._build_merkle_tree()

    @staticmethod
    def sha256(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_pair(left: str, right: str) -> str:
        return MerkleTree.sha256(left + right)

    def _build_merkle_tree(self) -> MerkleNode:
        """Строим дерево Меркла и возвращаем корневой узел."""
        new_leaves: List[MerkleNode] = []
        for i in range(0, len(self._leaves), 2):
            left = self._leaves[i]
            if i + 1 < len(self._leaves):
                right = self._leaves[i+1]
            else:
                right = deepcopy(left)  # Если нечётное количество, дублируем последний узел
            combined_hash = self.sha256(left.hash_value + right.hash_value)
            new_leaves.append(MerkleNode(left, right, combined_hash, left.tid + right.tid))
        self._leaves = new_leaves

        if len(self._leaves) == 1:
            return self._leaves[0]
        else:
            return self._build_merkle_tree()

    @property
    def root(self) -> Optional[MerkleNode]:
        return self._root

    def get_merkle_root(self) -> Optional[str]:
        return self.root.hash_value if self.root else None


def get_merkle_proof(tree: MerkleTree, tx: Transaction) -> Optional[List[Tuple[str, bool]]]:
    """Возвращает Merkle Proof для данной транзакции. Формат: список кортежей (хеш, слева ли узел)."""
    # Найдём лист (узел) с соответствующим хешем транзакции
    target_hash = tree.sha256(tx.json())

    # Функция для поиска нужного узла и построения пути
    def find_path(node: MerkleNode, current_path: List[Tuple[str, bool]]) -> Optional[List[Tuple[str, bool]]]:
        if not node.left and not node.right:  # Это лист
            if node.hash_value == target_hash:
                return current_path
            else:
                return None

        # Поиск в левом поддереве
        if node.left:
            left_path = find_path(node.left, current_path + [(node.right.hash_value if node.right else '', False)])
            if left_path:
                return left_path

        # Поиск в правом поддереве
        if node.right:
            right_path = find_path(node.right, current_path + [(node.left.hash_value if node.left else '', True)])
            if right_path:
                return right_path

        return None

    # Запускаем поиск пути от корня
    return find_path(tree.root, [])


import hashlib

from copy import deepcopy
from typing import List, Tuple, Optional


def calculate_sha256(data: str):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def hash_proof(proof: Tuple[str, List[str]]):
    next_hash, proof = proof
    total_hash = next_hash
    # concatenate all hashes
    for hash_value in sorted(proof):
        total_hash += hash_value
    return calculate_sha256(total_hash)

def is_valid(tree: MerkleTree, current_hash: str, proof: List[Tuple[str, bool]]) -> bool:
    for sibling_hash, is_left_sibling in proof[::-1]:
        if is_left_sibling:
            current_hash = MerkleTree.hash_pair(sibling_hash, current_hash)
        else:
            current_hash = MerkleTree.hash_pair(current_hash, sibling_hash)
    return current_hash == tree.get_merkle_root()


if __name__ == '__main__':
    test_transactions = [Transaction(i, 100*i, f"Payment {i}") for i in range(4)]
    merkle_tree = MerkleTree(test_transactions)
    print(f'Root: {merkle_tree.get_merkle_root()}')
    ts = test_transactions[0]
    proof = get_merkle_proof(merkle_tree, ts)
    print(is_valid(merkle_tree, MerkleTree.sha256(ts.json()), proof))
