import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import UUID
from sqlalchemy import Enum, types, func, update
from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
import enum


class Base(DeclarativeBase):
    pass


class OfferChoices(enum.Enum):
    Loanplus = "Loanplus"
    SgroshiCPA2 = "SgroshiCPA2"
    Novikredyty = "Novikredyty"
    TurboGroshi = "TurboGroshi"
    Crypsee = "Crypsee"
    Suncredit = "Suncredit"
    Lehko = "Lehko"
    Monto = "Monto"
    Limon = "Limon"
    Amigo = "Amigo"
    FirstCredit = "FirstCredit"
    Finsfera = "Finsfera"
    Pango = "Pango"
    Treba = "Treba"
    StarFin = "StarFin"
    BitCapital = "BitCapital"
    SgroshiCPL = "SgroshiCPL"
    LoviLave = "LoviLave"
    Prostocredit = "Prostocredit"
    Sloncredit = "Sloncredit"
    Clickcredit = "Clickcredit"
    Credos = "Credos"
    Dodam = "Dodam"
    SelfieCredit = "SelfieCredit"
    Egroshi = "Egroshi"
    Alexcredit = "Alexcredit"
    SgroshiCPA1 = "SgroshiCPA1"
    Tengo = "Tengo"
    Credit7 = "Credit7"
    Tpozyka = "Tpozyka"
    Creditkasa = "Creditkasa"
    Moneyveo = "Moneyveo"
    My_Credit = "MyCredit"
    Credit_Plus = "CreditPlus"
    Miloan = "Miloan"
    Avans = "AvansCredit"


class OfferWall(Base):
    __tablename__ = "offer_walls"

    token: Mapped[UUID] = mapped_column(types.UUID, default=uuid.uuid4, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(2000), default=None, nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), default=None, nullable=True)

    offer_assignments: Mapped[list["OfferWallOffer"]] = relationship("OfferWallOffer", back_populates="offer_wall")
    popup_assignments: Mapped[list["OfferWallPopupOffer"]] = relationship("OfferWallPopupOffer", back_populates="offer_wall")

    def __str__(self):
        return f"OfferWall {self.token}"

    async def add_offer(self, offer, db_session: AsyncSession, order=None):
        result = await db_session.execute(
            select(func.max(OfferWallOffer.order)).filter_by(offer_wall_id=self.token)
        )
        max_order = result.scalar() or 0
        if order is None:
            order = max_order + 1

        offer_wall_offer = OfferWallOffer(offer_wall=self, offer=offer, order=order)
        db_session.add(offer_wall_offer)
        await db_session.commit()

    async def reorder_offers(self, offer_order_list, db_session: AsyncSession):
        """Reorder offers based on a list of offer UUIDs"""
        async with db_session.begin():
            for index, offer_uuid in enumerate(offer_order_list):
                stmt = update(OfferWallOffer).where(
                    OfferWallOffer.offer_wall == self,
                    OfferWallOffer.offer.has(uuid=offer_uuid)
                ).values(order=index)

                await db_session.execute(stmt)

    async def get_offers(self, db_session: AsyncSession):
        """Get all offers in order (async version)"""
        result = await db_session.execute(
            select(OfferWallOffer)
        )

        offer_assignments = result.scalars().all()

        return [assignment.offer for assignment in offer_assignments]


class Offer(Base):
    __tablename__ = "offer"

    uuid: Mapped[UUID] = mapped_column(types.UUID, default=uuid.uuid4, primary_key=True)
    id: Mapped[int] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    name: Mapped[OfferChoices] = mapped_column(Enum(OfferChoices), unique=True)
    sum_to: Mapped[str | None] = mapped_column(String(100), default=None, nullable=True)
    term_to: Mapped[int | None] = mapped_column(Integer,default=None, nullable=True)
    percent_rate: Mapped[int | None] = mapped_column(Integer, default=None, nullable=True)

    wall_assignments: Mapped[list["OfferWallOffer"]] = relationship("OfferWallOffer", back_populates="offer")
    popup_assignments: Mapped[list["OfferWallPopupOffer"]] = relationship("OfferWallPopupOffer", back_populates="offer")

    def __repr__(self):
        return f"<OfferWallOffer(uuid={self.uuid}, name={self.name}, is_active={self.is_active})>"

    def __str__(self):
            return self.name

class OfferWallOffer(Base):
    __tablename__ = "offer_wall_offer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_wall_token: Mapped[UUID] = mapped_column(types.UUID, ForeignKey("offer_walls.token", ondelete="CASCADE"))
    offer_id: Mapped[UUID] = mapped_column(types.UUID, ForeignKey("offer.uuid", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, default=0)

    offer_wall: Mapped["OfferWall"] = relationship("OfferWall", back_populates="offer_assignments")
    offer: Mapped["Offer"] = relationship("Offer", back_populates="wall_assignments")

    def __str__(self):
        return f"{self.offer.name} in {self.offer_wall.token} (Order: {self.order})"


class OfferWallPopupOffer(Base):
    __tablename__ = 'offer_wall_popup_offer'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_wall_token: Mapped[UUID] = mapped_column(types.UUID, ForeignKey("offer_walls.token", ondelete="CASCADE"))
    offer_id: Mapped[UUID] = mapped_column(types.UUID, ForeignKey("offer.uuid", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, default=0)

    offer_wall: Mapped["OfferWall"] = relationship("OfferWall", back_populates="popup_assignments")
    offer: Mapped["Offer"] = relationship("Offer", back_populates="popup_assignments")

    __table_args__ = (
        UniqueConstraint('offer_wall_token', 'offer_id', name='uix_offer_wall_offer'),
    )

    def __str__(self):
        return f"{self.offer.name} in {self.offer_wall.token} (Order: {self.order})"
