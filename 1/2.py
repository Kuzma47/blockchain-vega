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
        # print([(node.tid, node.hash_value) for node in self._leaves])
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

    def get_merkle_proof(self, tx: Transaction):
        target_hash = MerkleTree.sha256(tx.json())

        def find_path(node: MerkleNode, current_path):
            if not node.left and not node.right:
                if node.hash_value == target_hash:
                    return current_path
                else:
                    return None

            if node.left:
                left_path = find_path(node.left, current_path + [(node.right.hash_value, node.right.tid) if node.right else ''])
                if left_path:
                    return left_path

            if node.right:
                right_path = find_path(node.right, current_path + [(node.left.hash_value, node.left.tid) if node.left else ''])
                if right_path:
                    return right_path

            return None

        return find_path(self.root, [])


def get_proof(tree: MerkleTree, transaction: Transaction):
    print(f'Proof for transaction {transaction.id}')
    for proof in tree.get_merkle_proof(transaction):
        print(f'\th({proof[1]}): {proof[0]}')


if __name__ == '__main__':
    tx1 = Transaction(1, 1.0, "Payment A")
    tx2 = Transaction(2, 20.0, "Payment B")
    tx3 = Transaction(3, 30.0, "Payment C")
    tx4 = Transaction(4, 40.0, "Payment D")
    tx5 = Transaction(5, 50.0, "Payment E")
    tx6 = Transaction(6, 60.0, "Payment F")
    tx7 = Transaction(7, 70.0, "Payment G")
    tx8 = Transaction(8, 80.0, "Payment H")

    transactions = [tx1, tx2, tx3, tx4, tx5, tx6, tx7, tx8]
    merkle_tree = MerkleTree(transactions)

    get_proof(merkle_tree, tx1)
