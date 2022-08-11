from flask_mail import Message

from istsosimport.env import flask_mail
from istsosimport.config.config_parser import config


def send_mail(recipients, subject, msg_html):
    """Envoi d'un email à l'aide de Flask_mail.

    .. :quickref:  Fonction générique d'envoi d'email.

    Parameters
    ----------
    recipients : str or [str]
        Chaine contenant des emails séparés par des virgules ou liste
        contenant des emails. Un email encadré par des chevrons peut être
        précédé d'un libellé qui sera utilisé lors de l'envoi.

    subject : str
        Sujet de l'email.
    msg_html : str
        Contenu de l'eamil au format HTML.

    Returns
    -------
    void
        L'email est envoyé. Aucun retour.
    """

    with flask_mail.connect() as conn:
        mail_sender = config["MAIL_CONFIG"].get("MAIL_DEFAULT_SENDER")
        if not mail_sender:
            mail_sender = config["MAIL_CONFIG"]["MAIL_USERNAME"]
        msg = Message(subject, sender=mail_sender, recipients=[recipients])
        msg.html = msg_html
        conn.send(msg)
